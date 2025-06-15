import base64
import hashlib
from math import ceil
import os
import time # we can remove this, this is just for testing

class CAE:
    """
    A class to encapsulate the Cellular Automata Encryption (CAE) system.
    This implementation uses Counter (CTR) mode for secure encryption of any length.
    """
    def __init__(self, iterations=1_000, grid_size=16, generations=10):
        self.iterations = iterations
        self.grid_size = grid_size
        self.block_size = grid_size * grid_size  # 16x16 = 256 bytes
        self.master_key_length = self.block_size # Master key must match block size
        self.generations = generations
        self.salt_bytes = 16

    def _stretch_key(self, password: bytes, salt: bytes, iteration: int, key_length: int) -> bytes:
        """Stretches the password and salt to create a master key of the desired length."""
        master_key = b''
        digest_size = hashlib.sha256().digest_size
        num_blocks = ceil(key_length / digest_size)

        for block_index in range(1, num_blocks + 1):
            stretched_key_block = hashlib.sha256(password + salt + block_index.to_bytes(4, 'big')).digest()
            for _ in range(iteration):
                stretched_key_block = hashlib.sha256(stretched_key_block + password + salt).digest()
            master_key += stretched_key_block

        return master_key[:key_length]

    def _apply_counter(self, key: bytes, counter: int) -> bytes:
        """Applies a counter to a key to produce a unique seed for each block (CTR mode)."""
        temp_key = bytearray(key)
        counter_bytes = counter.to_bytes(8, 'big')

        # XOR the counter into the last 8 bytes of the key copy
        for i in range(8):
            temp_key[self.block_size - 8 + i] ^= counter_bytes[i]

        return bytes(temp_key)

    def _convert_bytes_to_grid(self, byte_chunk: bytes) -> list[list[int]]:
        """Converts a 256-byte chunk into a 16x16 grid of integers."""
        return [[byte_chunk[i * self.grid_size + j] for j in range(self.grid_size)] for i in range(self.grid_size)]

    def _apply_ca_rules(self, kernel: list[list[int]], generation_num: int) -> int:
        """Calculates a cell's next state based on its 3x3 kernel and custom rules."""
        core_value = kernel[1][1]

        live_neighbors = 0
        for i in range(3):
            for j in range(3):
                if i == 1 and j == 1:
                    continue
                if kernel[i][j] > 128:
                    live_neighbors += 1

        if core_value > 128:
            if live_neighbors in [2, 3]:
                new_value = min(255, core_value + live_neighbors)
            else:
                new_value = max(0, core_value - live_neighbors * 2)
        else:
            if live_neighbors == 3:
                new_value = min(255, core_value + live_neighbors * 10)
            else:
                new_value = (core_value + live_neighbors * generation_num) % 256

        return new_value

    def _run_ca_simulation(self, seed_grid: list[list[int]]) -> list[list[int]]:
        """Runs the CA simulation for a fixed number of generations."""
        current_grid = seed_grid

        for generation_num in range(1, self.generations + 1):
            new_grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    kernel = [[0 for _ in range(3)] for _ in range(3)]
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            neighbor_r = (r + i) % self.grid_size
                            neighbor_c = (c + j) % self.grid_size
                            kernel[i + 1][j + 1] = current_grid[neighbor_r][neighbor_c]

                    new_grid[r][c] = self._apply_ca_rules(kernel, generation_num)
            current_grid = new_grid

        return current_grid

    def _flatten_grid_to_bytes(self, grid: list[list[int]]) -> bytes:
        """Converts a 16x16 grid back into a 256-byte keystream."""
        return bytes([cell for row in grid for cell in row])

    def encrypt(self, plaintext: str, password: str) -> str:
        """Encrypts a plaintext string using CTR mode."""
        # 1. Setup
        plaintext_bytes = plaintext.encode('utf-8')
        salt = os.urandom(self.salt_bytes)
        master_key = self._stretch_key(password.encode('utf-8'), salt, self.iterations, self.master_key_length)

        ciphertext = b''
        # 2. Loop through plaintext in blocks
        for i in range(0, len(plaintext_bytes), self.block_size):
            plaintext_block = plaintext_bytes[i:i + self.block_size]
            block_counter = i // self.block_size

            # 3. Generate unique keystream for this block
            seed = self._apply_counter(master_key, block_counter)
            initial_grid = self._convert_bytes_to_grid(seed)
            final_grid = self._run_ca_simulation(initial_grid)
            keystream = self._flatten_grid_to_bytes(final_grid)

            # 4. XOR the plaintext block with the keystream
            encrypted_block = bytes([p_byte ^ k_byte for p_byte, k_byte in zip(plaintext_block, keystream)])
            ciphertext += encrypted_block

        # 5. Return the salt concatenated with the final ciphertext
        return base64.b64encode(salt + ciphertext).decode('utf-8')

    def decrypt(self, encrypted_text: str, password: str) -> str:
        """Decrypts data encrypted with this system."""
        # 1. Setup
        byte_data = base64.b64decode(encrypted_text)
        salt = byte_data[:self.salt_bytes]
        ciphertext = byte_data[self.salt_bytes:]
        master_key = self._stretch_key(password.encode('utf-8'), salt, self.iterations, self.master_key_length)

        decrypted_bytes = b''
        # 2. Loop through ciphertext in blocks (same process as encryption)
        for i in range(0, len(ciphertext), self.block_size):
            ciphertext_block = ciphertext[i:i + self.block_size]
            block_counter = i // self.block_size

            # 3. Re-generate the exact same unique keystream for this block
            seed_for_block = self._apply_counter(master_key, block_counter)
            initial_grid = self._convert_bytes_to_grid(seed_for_block)
            final_grid = self._run_ca_simulation(initial_grid)
            keystream_block = self._flatten_grid_to_bytes(final_grid)

            # 4. XOR the ciphertext block with the keystream to get the original plaintext
            decrypted_block = bytes([c_byte ^ k_byte for c_byte, k_byte in zip(ciphertext_block, keystream_block)])
            decrypted_bytes += decrypted_block

        # 5. Decode the final bytes back to a string
        return decrypted_bytes.decode('utf-8')

def test():
    cae_cipher = CAE(iterations=1_000_000_000)

    # --- message and password ---
    my_password = "a_very_secure_password_123!"
    my_message = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum consectetur sit amet ex quis tristique. Vestibulum suscipit dui vestibulum, porta lectus nec, commodo ex. Praesent commodo ex in tempor dapibus. Integer mollis elementum neque, quis accumsan est lobortis et. Aliquam fermentum enim mollis diam consequat imperdiet et sed felis. Suspendisse aliquet molestie tortor a semper. Mauris gravida dictum justo et pretium. Sed hendrerit mauris nulla, in scelerisque nunc auctor at. Mauris a porta elit. Praesent posuere massa et orci porta efficitur. Phasellus ac posuere lorem. Sed ullamcorper, enim ut mattis fringilla, libero erat laoreet nisi, quis sollicitudin neque mi ut purus.

    Praesent pulvinar nec justo sit amet varius. Ut vel enim id mauris luctus iaculis quis sit amet orci. Nulla non erat sed massa tempor posuere eu id velit. Duis eleifend convallis dolor, id lacinia lectus accumsan nec. Praesent tempor neque eu ante pretium sodales. Mauris venenatis nisl eget lobortis egestas. Cras dolor mi, tristique et cursus a, rhoncus eget quam. Nam eleifend nulla nec lorem ullamcorper, sed consequat lorem ullamcorper. Proin elementum velit eu risus lobortis ultrices ut id libero. Proin ante sapien, rhoncus vel accumsan non, vestibulum et eros.

    Phasellus dictum accumsan lectus, at fermentum lorem condimentum eget. Etiam aliquet vestibulum nisi, ac blandit sem euismod ut. Vestibulum eget elementum erat, sed rhoncus sapien. Ut vehicula, leo vel rhoncus facilisis, sem leo malesuada erat, sed blandit purus lectus non mauris. Nulla facilisi. Curabitur faucibus semper ante ac fringilla. Nam sollicitudin tortor ante, ac dictum enim facilisis non. Pellentesque nec dui eget sapien accumsan sagittis. Fusce pellentesque urna in eros tincidunt rhoncus. Sed vehicula ipsum tellus, eget lacinia est pharetra dapibus. Sed egestas hendrerit ante nec lacinia.

    Maecenas ultricies lacus ac vestibulum sagittis. Proin tempus feugiat ligula at congue. Fusce tellus elit, malesuada eget hendrerit vel, dignissim eu dui. Nullam aliquam, justo eu eleifend venenatis, neque dui imperdiet urna, eu luctus risus risus viverra sapien. Donec ut ligula et dui facilisis pellentesque. Fusce ac blandit ex. Curabitur in condimentum nulla, sit amet consectetur augue. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae;

    Fusce quis lectus sollicitudin, interdum ipsum a, tempor nibh. Praesent vel tristique nisl. Nulla molestie diam elit, in tempus est ultricies et. In hac habitasse platea dictumst. Donec eget posuere massa, aliquet tristique sapien. Vivamus lorem urna, egestas ut purus nec, blandit gravida est. Praesent nec nisi rutrum, eleifend urna ut, eleifend dui. Duis a justo non eros finibus aliquet a eu turpis.

    Donec volutpat blandit dui ut maximus. Aliquam eget sapien nec dui eleifend scelerisque at id felis. Integer ac nibh augue. In tincidunt interdum luctus. Nulla vulputate in erat ac sollicitudin. Duis non eros eget tellus pharetra consectetur at sit amet velit. Pellentesque pellentesque egestas hendrerit. Proin in hendrerit enim.

    Donec ullamcorper, ipsum eget placerat commodo, neque dui interdum mi, dignissim tristique eros magna accumsan ante. Curabitur dignissim metus id molestie ultrices. Vivamus id egestas mauris. Sed et interdum mauris. Fusce vel justo et dui commodo dignissim ac nec mi. In lacinia aliquet imperdiet. Ut vitae ligula at nulla vestibulum scelerisque ut eu metus. Fusce lorem orci, auctor vitae ante a, laoreet sollicitudin dui. Nunc sodales ipsum risus, sed ultrices est gravida quis. Fusce lacinia, ipsum vitae mollis blandit, lectus metus ullamcorper justo, quis congue nunc lectus eu ex. Pellentesque posuere sapien mi, in porttitor ipsum gravida et. Nunc viverra eu sem id pellentesque. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.

    Nunc nec eleifend ante. Curabitur dictum sit amet lectus rutrum lacinia. Nam ut dapibus mi, sed vestibulum urna. Fusce vitae ipsum at odio vehicula porta vitae quis orci. Ut accumsan elit venenatis quam tempor, vitae aliquet diam ornare. Vestibulum at sagittis est. Curabitur consectetur diam ut neque porttitor, ac consectetur augue porta. Pellentesque blandit, odio vel tincidunt porta, elit augue imperdiet urna, vel fermentum sem neque at urna. Nunc vitae viverra lorem. In egestas arcu eros, sit amet egestas sapien pulvinar et. Phasellus volutpat, arcu a scelerisque molestie, elit eros semper libero, ac sodales nibh diam ac nulla.

    In tincidunt ex vehicula justo euismod, sed condimentum diam semper. Ut vel porta orci, a maximus risus. Donec scelerisque, nisi id elementum dapibus, est metus mollis metus, ac porta purus neque ac magna. Donec a consequat velit. Vivamus et orci non sem molestie dictum at ut erat. Aliquam lectus nibh, tincidunt eget suscipit non, sollicitudin et magna. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Phasellus est neque, facilisis condimentum justo quis, finibus mattis enim. Aliquam viverra molestie volutpat. Suspendisse lectus arcu, ultricies quis urna vel, ornare suscipit quam. Donec commodo ex ac libero varius, sed bibendum urna rutrum. Curabitur facilisis ultricies tortor, quis porttitor justo sodales dapibus. Maecenas pretium ligula nec risus tristique ultricies. Curabitur et consectetur ligula. Aenean egestas ligula lacus, quis ullamcorper ex eleifend ac.

    Phasellus sed neque facilisis turpis tempor dictum nec in ipsum. Praesent egestas neque ipsum, et egestas metus semper sagittis. Nunc sit amet pellentesque mi. Aenean nulla purus, lobortis sed sollicitudin eu, dapibus vitae neque. Duis porta nisi sit amet lacus sagittis posuere. Donec eu tellus non dolor efficitur cursus eget in leo. Proin mi enim, laoreet vitae maximus at, lobortis sit amet nisi."""

    print("--- ENCRYPTION ---")
    print(f"Original Message:\n'{my_message}'\n")

    start_time_enc = time.perf_counter()
    encrypted_blob = cae_cipher.encrypt(my_message, my_password)
    end_time_enc = time.perf_counter()
    encryption_time = end_time_enc - start_time_enc
    print(f"Encrypted data:\n{encrypted_blob}\n")
    print(f"Encryption took: {encryption_time:.4f} seconds")


    print("--- DECRYPTION ---")
    try:
        start_time_dec = time.perf_counter()
        decrypted_message = cae_cipher.decrypt(encrypted_blob, my_password)
        end_time_dec = time.perf_counter()
        decryption_time = end_time_dec - start_time_dec
        print(f"Decrypted Message:\n'{decrypted_message}'\n")
        print(f"Decryption took: {decryption_time:.4f} seconds\n")

        if my_message == decrypted_message:
            print("SUCCESS: Decryption successful, messages match.")
        else:
            print("FAILURE: Messages do not match.")

    except Exception as e:
        print(f"An error occurred during decryption: {e}")

if __name__ == "__main__":
    test()
    '''
    ========== Test Benchmark ==========
    Lorem ipsum 10 paragraph (3 times) 
    in average
    1 * 10^0 iter:
        encrypt: 2.369167 seconds
        decrypt: 2.438133 seconds
    1 * 10^3 iter:
        encrypt: 2.209667 seconds
        decrypt: 2.205567 seconds
    1 * 10^6 iter:
        encrypt: 9.123033 seconds
        decrypt: 9.365000 seconds
    1 * 10^9 iter: (Not Recommended)
        encrypt: Too Long
        decrypt: Too Long
    ====================================
    '''

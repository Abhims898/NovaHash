import math

class NebulaHash:
    @staticmethod
    def compute(input_str, hash_length=32):
        if not isinstance(input_str, str):
            input_str = str(input_str)
        
        if hash_length < 8 or hash_length > 64 or hash_length % 8 != 0:
            raise ValueError("Hash length must be between 8-64 and multiple of 8")
        
        # Initialization with mathematical constants
        h = [
            int((math.pi * 2**32) % 2**32),
            int((math.e * 2**32) % 2**32),
            int((1.61803398875 * 2**32) % 2**32),  # Golden ratio
            int((math.sqrt(2) * 2**32) % 2**32)
        ]
        
        prime1 = 2654435761
        prime2 = 2246822519
        
        # Process each character
        for i, char in enumerate(input_str):
            char_code = ord(char)
            position = i + 1  # Avoid zero
            
            # Dynamic operations
            segment = i % 4
            rotated = ((char_code << (position % 7)) | (char_code >> (8 - (position % 7)))) & 0xFF
            h[segment] = (h[segment] + (rotated * prime1)) % 2**32
            h[segment] ^= ((h[(segment + 1) % 4] + position) * prime2)
            h[segment] = (h[segment] >> 3) | (h[segment] << (32 - 3))  # Rotate right 3 bits
        
        # Final mixing
        h[0] = (h[0] + h[2] + prime1) % 2**32
        h[1] = (h[1] + h[3] + prime2) % 2**32
        h[2] = (h[2] + h[0] * prime1) % 2**32
        h[3] = (h[3] + h[1] * prime2) % 2**32
        
        # Combine and format
        combined = (h[0] ^ h[1] ^ h[2] ^ h[3]) % 2**32
        hex_hash = f"{combined:08x}"
        
        # Extend to desired length
        while len(hex_hash) < hash_length:
            hex_hash += f"{(combined + len(hex_hash)):08x}"
        
        return hex_hash[:hash_length]

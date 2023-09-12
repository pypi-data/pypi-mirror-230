import random
import time
import hashlib
import string

def eid1(node_id):
    """
    Generate and format a version 1 UUID (Eid1).

    Args:
        node_id (int): Node identifier.

    Returns:
        str: Formatted version 1 UUID.

    Usage:
        uuid = eid1(0x123456789abc)
    """
    timestamp = int(time.time() * 1e9)
    clock_seq = random.getrandbits(14)
    uuid = (timestamp << 64) | (clock_seq << 50) | 0x1000000000000000
    uuid |= node_id
    return formateid(uuid)

def eid2(node_id, domain_id):
    """
    Generate and format a version 2 UUID (Eid2).

    Args:
        node_id (int): Node identifier.
        domain_id (int): Domain identifier.

    Returns:
        str: Formatted version 2 UUID.

    Usage:
        uuid = eid2(0x123456789abc, 0xabcdef)
    """
    timestamp = int(time.time())
    clock_seq = random.getrandbits(14)
    uuid = (timestamp << 32) | (clock_seq << 16) | 0x2000
    uuid |= (node_id << 48) | domain_id
    return formateid(uuid)

def eid3(name):
    """
    Generate and format a version 3 UUID (Eid3).

    Args:
        name (str): Name for UUID generation.

    Returns:
        str: Formatted version 3 UUID.

    Usage:
        uuid = eid3('example_name')
    """
    namespace_uuid = eid1(node_id=0x123456789abc)
    hashed_name = hashlib.md5((namespace_uuid + name).encode('utf-8')).hexdigest()
    uuid = formatAdvance(hashed_name, version=3)
    return uuid

def eid4():
    """
    Generate and format a version 4 UUID (Eid4).

    Returns:
        str: Formatted version 4 UUID.

    Usage:
        uuid = eid4()
    """
    uuid = random.getrandbits(128)
    return formateid(uuid)

def eid5(namespace, name):
    """
    Generate and format a version 5 UUID (Eid5).

    Args:
        namespace (str): Namespace for UUID generation.
        name (str): Name for UUID generation.

    Returns:
        str: Formatted version 5 UUID.

    Usage:
        uuid = eid5('example-namespace', 'example_name')
    """
    namespace_uuid = eid1(node_id=0x123456789abc)
    hashed_name = hashlib.sha1((namespace_uuid + name).encode('utf-8')).hexdigest()
    namespace_hex = namespace.replace('-', '')
    uuid = hashed_name[:16] + '-' + hashed_name[16:20] + '-5' + hashed_name[21:24] + '-' + namespace_hex[:4] + '-' + namespace_hex[4:16]
    return uuid

def defaultend():
    """
    Generate and format a default version UUID.

    Returns:
        str: Formatted default version UUID.

    Usage:
        uuid = defaultend()
    """
    timestamp = int(time.time())
    random_part = random.getrandbits(64)
    uuid = (timestamp << 64) | random_part
    return (uuid)

def formatAdvance(uuid_str, version):
    """
    Format a UUID string with a specified version.

    Args:
        uuid_str (str): UUID string to format.
        version (int): UUID version.

    Returns:
        str: Formatted UUID.

    Usage:
        formatted_uuid = formatAdvance('...', version=3)
    """
    parts = [uuid_str[:8], uuid_str[8:12], str(version) + uuid_str[13:16], uuid_str[16:20], uuid_str[20:]]
    return '-'.join(parts)

def formateid(uuid):
    """
    Format a UUID from its integer representation.

    Args:
        uuid (int): Integer representation of a UUID.

    Returns:
        str: Formatted UUID.

    Usage:
        formatted_uuid = formateid(1234567890)
    """
    uuid_str = f"{uuid:032x}"
    formatted_uuid = f"{uuid_str[:8]}-{uuid_str[8:12]}-{uuid_str[12:16]}-{uuid_str[16:20]}-{uuid_str[20:]}"
    return formatted_uuid

def geneid(length=10):
    """
    Generate a random string identifier with a specified length.

    Args:
        length (int): Length of the generated identifier.

    Returns:
        str: Randomly generated identifier.

    Usage:
        identifier = geneid(length=8)
    """
    if length < 2:
        raise ValueError("Length must be at least 2.")
    starting_char = random.choice(string.ascii_lowercase)
    remaining_length = length - 2
    random_digits = ''.join(random.choice(string.digits) for _ in range(remaining_length))
    unique_id = starting_char + '-' + random_digits
    return unique_id

class Eid:
    def __init__(self, node=None, clock_seq=None):
        """
        Initialize the Eid (Extended UUID) generator.

        Args:
            node (int): Node identifier.
            clock_seq (int): Clock sequence.

        Usage:
            eid = Eid(node=0x123456789abc, clock_seq=0xabcdef)
        """
        self.node = node if node is not None else random.getrandbits(48)
        self.clock_seq = clock_seq if clock_seq is not None else random.getrandbits(14)
        self.variant_bits = 0b1000

    def chip1(self):
        """
        Generate and format a version 1 UUID (Eid1).

        Returns:
            str: Formatted version 1 UUID.

        Usage:
            uuid = eid.chip1()
        """
        timestamp = int(time.time() * 1e7) + 0x01b21dd213814000
        timestamp_hex = format(timestamp, '032x')
        clock_seq_hex = format(self.clock_seq, '04x')
        node_hex = format(self.node, '012x')
        uuid = f"{timestamp_hex[:8]}-{timestamp_hex[8:12]}-{timestamp_hex[12:16]}-{clock_seq_hex[0]}{timestamp_hex[16:]}-{node_hex}"
        return uuid

    def chip3(self, name, namespace_uuid):
        """
        Generate and format a version 3 UUID (Eid3).

        Args:
            name (str): Name for UUID generation.
            namespace_uuid (str): Namespace UUID.

        Returns:
            str: Formatted version 3 UUID.

        Usage:
            uuid = eid.chip3('example_name', 'namespace-uuid')
        """
        hash_obj = hashlib.sha1(namespace_uuid.encode('utf-8') + name.encode('utf-8'))
        hash_bytes = hash_obj.digest()
        hash_int = int.from_bytes(hash_bytes, 'big')
        uuid = f"{hash_int:032x}"
        return uuid

    def chip4(self):
        """
        Generate and format a version 4 UUID (Eid4).

        Returns:
            str: Formatted version 4 UUID.

        Usage:
            uuid = eid.chip4()
        """
        random_bits_hex = format(random.getrandbits(128), '032x')
        uuid = f"{random_bits_hex[:8]}-{random_bits_hex[8:12]}-4{random_bits_hex[13:16]}-{self.variant_bits}{random_bits_hex[16:20]}-{random_bits_hex[20:]}"
        return uuid

    def chip2(self, domain=None):
        """
        Generate and format a version 2 UUID (Eid2).

        Args:
            domain (str): Domain identifier.

        Returns:
            str: Formatted version 2 UUID.

        Usage:
            uuid = eid.chip2('example-domain')
        """
        if domain is None:
            raise ValueError("Domain is required for version 2 UUID.")
        timestamp = int(time.time() * 1e7) + 0x01b21dd213814000
        timestamp_hex = format(timestamp, '032x')
        clock_seq_hex = format(self.clock_seq, '04x')
        node_hex = format(self.node, '012x')
        uuid = f"{domain[:8]}-{timestamp_hex[8:12]}-{timestamp_hex[12:16]}-{clock_seq_hex[0]}{timestamp_hex[16:]}-{node_hex}"
        return uuid

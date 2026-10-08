import hashlib, struct, re, sys

MSG   = "Jarar Coin 08/Oct/2026 - Jarar Records"
NTIME = 1791435000
NBITS = 0x207fffff
FILE  = "src/kernel/chainparams.cpp"
OLD_HASH   = "00000000da84f2bafbbc53dee25a72ae507ff4914b867c565be350b0da8bf043"
OLD_MERKLE = "7aa0a7ae1e223414cb807e40cd57e667b718e42aaf9306db9102fe28912b7b4e"

def sha256d(b):
    return hashlib.sha256(hashlib.sha256(b).digest()).digest()

def push(d):
    return (bytes([len(d)]) if len(d) < 76 else b"\x4c" + bytes([len(d)])) + d

def genesis_hashes(msg, ntime, nbits, search=True, nonce=0):
    script_sig = bytes.fromhex("04ffff001d0104") + push(msg.encode())
    spk = push(b"\x00" * 33) + b"\xac"
    tx = (struct.pack("<I", 1) + b"\x01" + b"\x00" * 32 + b"\xff" * 4
          + bytes([len(script_sig)]) + script_sig + b"\xff" * 4
          + b"\x01" + struct.pack("<Q", 50 * 100000000)
          + bytes([len(spk)]) + spk + b"\x00" * 4)
    merkle = sha256d(tx)
    exp, mant = nbits >> 24, nbits & 0xFFFFFF
    target = mant << (8 * (exp - 3))
    while True:
        hdr = (struct.pack("<I", 1) + b"\x00" * 32 + merkle
               + struct.pack("<III", ntime, nbits, nonce))
        h = sha256d(hdr)
        if not search or int.from_bytes(h, "little") <= target:
            return nonce, h[::-1].hex(), merkle[::-1].hex()
        nonce += 1

def patch(nonce, new_hash, new_merkle):
    src = open(FILE).read()
    a = src.index("class CTestNet4Params")
    b = src.index("\n};\n", a)
    blk = src[a:b]
    def sub(pattern, repl):
        nonlocal blk
        blk, n = re.subn(pattern, repl, blk)
        if n == 0:
            sys.exit("ERROR: yeh hissa nahi mila: " + pattern)
    sub(r'(const char\* testnet4_genesis_msg = )"[^"]*";', lambda m: m.group(1) + '"' + MSG + '";')
    sub(r'(testnet4_genesis_script,\s*)\d+,(\s*)\d+,(\s*)0x[0-9a-fA-F]+,',
        lambda m: "%s%d,%s%d,%s0x%08x," % (m.group(1), NTIME, m.group(2), nonce, m.group(3), NBITS))
    sub(r'(consensus\.powLimit = )uint256\{"[0-9a-f]+"\};',
        lambda m: m.group(1) + 'uint256{"7fffff0000000000000000000000000000000000000000000000000000000000"};')
    sub(r'(consensus\.nMinimumChainWork = )uint256\{"[0-9a-f]+"\};', lambda m: m.group(1) + "uint256{};")
    sub(r'(consensus\.defaultAssumeValid = )uint256\{"[0-9a-f]+"\};', lambda m: m.group(1) + "uint256{};")
    sub(OLD_HASH, new_hash)
    sub(OLD_MERKLE, new_merkle)
    open(FILE, "w").write(src[:a] + blk + src[b:])

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        t = genesis_hashes("03/May/2024 000000000000000000001ebd58c244970b3aa9d783bb001011fbe8ea8e98e00e",
                           1714777860, 0x1d00ffff, search=False, nonce=393743547)
        print(t[1] == OLD_HASH and t[2] == OLD_MERKLE and "SELFTEST OK" or "SELFTEST FAIL")
        sys.exit()
    nonce, h, m = genesis_hashes(MSG, NTIME, NBITS)
    print("nonce       :", nonce)
    print("genesis hash:", h)
    print("merkle root :", m)
    patch(nonce, h, m)
    print("chainparams.cpp update ho gayi.")

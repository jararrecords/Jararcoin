import re, sys
from genesis import genesis_hashes, MSG

FILE = "src/kernel/chainparams.cpp"
src = open(FILE).read()
a = src.index("class CMainParams")
b = src.index("\n};\n", a)
blk = src[a:b]

if "jarar_genesis_msg" in blk:
    sys.exit("Yeh pehle hi lag chuka hai, kuch badla nahi.")

pat = r'genesis = CreateGenesisBlock\((\d+), (\d+), (0x[0-9a-fA-F]+), 1, 50 \* COIN\);'
m = re.search(pat, blk)
if not m:
    sys.exit("ERROR: mainnet ki genesis line nahi mili. Mujhe bata dein.")
ntime, nbits = int(m.group(1)), int(m.group(3), 16)

print("Nonce dhoondh raha hoon (kuch seconds lagenge)...")
nonce, h, mr = genesis_hashes(MSG, ntime, nbits)

new_line = ('const char* jarar_genesis_msg = "%s";\n'
            '        const CScript jarar_genesis_script = CScript() << "%s"_hex << OP_CHECKSIG;\n'
            '        genesis = CreateGenesisBlock(jarar_genesis_msg, jarar_genesis_script, %d, %d, 0x%08x, 1, 50 * COIN);'
            % (MSG, "00" * 33, ntime, nonce, nbits))
blk, n1 = re.subn(pat, lambda x: new_line, blk)
blk, n2 = re.subn(r'(assert\(consensus\.hashGenesisBlock == uint256\{")[0-9a-f]+("\}\);)',
                  lambda x: x.group(1) + h + x.group(2), blk)
blk, n3 = re.subn(r'(assert\(genesis\.hashMerkleRoot == uint256\{")[0-9a-f]+("\}\);)',
                  lambda x: x.group(1) + mr + x.group(2), blk)
if not (n1 == n2 == n3 == 1):
    sys.exit("ERROR: kuch lines nahi mili (%d %d %d). File ko haath nahi lagaya." % (n1, n2, n3))

open(FILE, "w").write(src[:a] + blk + src[b:])
print("nonce       :", nonce)
print("genesis hash:", h)
print("merkle root :", mr)
print("chainparams.cpp (mainnet genesis) update ho gayi.")

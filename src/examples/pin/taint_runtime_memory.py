
# Using: $ ./triton ./src/examples/pin/taint_runtime_memory.py ./src/samples/crackmes/crackme_xor a

from triton  import *
from pintool import *

GREEN = "\033[92m"
ENDC  = "\033[0m"


# 0x40058b: movzx eax, byte ptr [rax]
#
# When the instruction located in 0x40058b is executed,
# we taint the memory that RAX holds.
def cbeforeSymProc(instruction):
    if instruction.getAddress() == 0x40058b:
        rax = getCurrentRegisterValue(REG.RAX)
        taintAddr(rax)


def cafter(instruction):
    print '%#x: %s' %(instruction.getAddress(), instruction.getDisassembly())
    for se in instruction.getSymbolicExpressions():
        if se.isTainted() == True:
            print '\t -> %s%s%s' %(GREEN, se.getAst(), ENDC)
        else:
            print '\t -> %s' %(se.getAst())
    print


if __name__ == '__main__':

    # Set architecture
    setArchitecture(ARCH.X86_64)

    # Start the symbolic analysis from the 'check' function
    startAnalysisFromSymbol('check')

    addCallback(cbeforeSymProc, CALLBACK.BEFORE_SYMPROC)
    addCallback(cafter, CALLBACK.AFTER)

    # Run the instrumentation - Never returns
    runProgram()

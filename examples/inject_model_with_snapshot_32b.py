
# $ ./triton ./examples/inject_model_with_snapshot_32b.py ./samples/32bits/crackme_xor a
# [+] Take a snapshot at the prologue of the function
# [+] Still not the good password. Restore snapshot.
# [+] Inject the character 'e' in memory
# [+] Still not the good password. Restore snapshot.
# [+] Inject the character 'e' in memory
# [+] Inject the character 'l' in memory
# [+] Still not the good password. Restore snapshot.
# [+] Inject the character 'e' in memory
# [+] Inject the character 'l' in memory
# [+] Inject the character 'i' in memory
# [+] Still not the good password. Restore snapshot.
# [+] Inject the character 'e' in memory
# [+] Inject the character 'l' in memory
# [+] Inject the character 'i' in memory
# [+] Inject the character 't' in memory
# [+] Still not the good password. Restore snapshot.
# [+] Inject the character 'e' in memory
# [+] Inject the character 'l' in memory
# [+] Inject the character 'i' in memory
# [+] Inject the character 't' in memory
# [+] Inject the character 'e' in memory
# [+] Good password found!
# Win
# [+] Analysis done!


from    triton import *
import  smt2lib

password  = dict()
symVarMem = None


def csym(instruction):
    # 0x40058b: movzx eax, byte ptr [rax]
    if instruction.getAddress() == 0x8048412:
        global symVarMem
        symVarMem = getRegValue(IDREF.REG.EAX)
    return


def cafter(instruction):

    # 0x40058b: movzx eax, byte ptr [rax]
    if instruction.getAddress() == 0x8048412:
        v = convertRegToSymVar(IDREF.REG.EAX, 32)
        #print "Concrete value:\t%s\t%c" % (v, v.getConcreteValue())

    # 0x4005ae: cmp ecx, eax
    if instruction.getAddress() == 0x8048431:
        zfId    = getRegSymbolicID(IDREF.FLAG.ZF)
        zfExpr  = getFullExpression(getSymExpr(zfId).getAst())
        expr    = smt2lib.smtAssert(smt2lib.equal(zfExpr, smt2lib.bvtrue())) # (assert (= zf True))
        models  = getModel(expr)
        global password
        for k, v in models.items():
            password.update({symVarMem: v})

    return


def cbefore(instruction):

    # Prologue of the function
    global snapshot
    if instruction.getAddress() == 0x80483fb and isSnapshotEnabled() == False:
        takeSnapshot()
        print '[+] Take a snapshot at the prologue of the function'
        return

    # 0x40058b: movzx eax, byte ptr [rax]
    if instruction.getAddress() == 0x8048412:
        rax = getRegValue(IDREF.REG.EAX)
        if rax in password:
            setMemValue(rax, 1, password[rax])
            print '[+] Inject the character \'%c\' in memory' %(chr(password[rax]))

    # Epilogue of the function
    if instruction.getAddress() == 0x804844b:
        rax = getRegValue(IDREF.REG.EAX)
        # The function returns 0 if the password is valid
        # So, we restore the snapshot until this function
        # returns something else than 0.
        if rax != 0:
            print '[+] Still not the good password. Restore snapshot.'
            restoreSnapshot()
        else:
            print '[+] Good password found!'
            disableSnapshot()
        return
    return


def fini():
    print '[+] Analysis done!'


if __name__ == '__main__':

    # Start the symbolic analysis from the 'check' function
    startAnalysisFromSymbol('check')

    addCallback(cafter,         IDREF.CALLBACK.AFTER)
    addCallback(cbefore,        IDREF.CALLBACK.BEFORE)
    addCallback(csym,           IDREF.CALLBACK.BEFORE_SYMPROC)
    addCallback(fini,           IDREF.CALLBACK.FINI)

    # Run the instrumentation - Never returns
    runProgram()



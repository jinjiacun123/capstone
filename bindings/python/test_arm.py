#!/usr/bin/env python

# Capstone Python bindings, by Nguyen Anh Quynnh <aquynh@gmail.com>

from __future__ import print_function
from capstone import *
from capstone.arm import *
from xprint import to_hex, to_x_32


ARM_CODE = b"\x86\x48\x60\xf4\xED\xFF\xFF\xEB\x04\xe0\x2d\xe5\x00\x00\x00\x00\xe0\x83\x22\xe5\xf1\x02\x03\x0e\x00\x00\xa0\xe3\x02\x30\xc1\xe7\x00\x00\x53\xe3\x00\x02\x01\xf1\x05\x40\xd0\xe8\xf4\x80\x00\x00"
ARM_CODE2 = b"\xd1\xe8\x00\xf0\xf0\x24\x04\x07\x1f\x3c\xf2\xc0\x00\x00\x4f\xf0\x00\x01\x46\x6c"
THUMB_CODE = b"\x70\x47\xeb\x46\x83\xb0\xc9\x68\x1f\xb1\x30\xbf\xaf\xf3\x20\x84\x52\xf8\x23\xf0"
THUMB_CODE2 = b"\x4f\xf0\x00\x01\xbd\xe8\x00\x88\xd1\xe8\x00\xf0\x18\xbf\xad\xbf\xf3\xff\x0b\x0c\x86\xf3\x00\x89\x80\xf3\x00\x8c\x4f\xfa\x99\xf6\xd0\xff\xa2\x01"
THUMB_MCLASS = b"\xef\xf3\x02\x80"
ARMV8 = b"\xe0\x3b\xb2\xee\x42\x00\x01\xe1\x51\xf0\x7f\xf5"

all_tests = (
        (CS_ARCH_ARM, CS_MODE_ARM, ARM_CODE, "ARM", None),
        (CS_ARCH_ARM, CS_MODE_THUMB, THUMB_CODE, "Thumb", None),
        (CS_ARCH_ARM, CS_MODE_THUMB, ARM_CODE2, "Thumb-mixed", None),
        (CS_ARCH_ARM, CS_MODE_THUMB, THUMB_CODE2, "Thumb-2 & register named with numbers", CS_OPT_SYNTAX_NOREGNAME),
        (CS_ARCH_ARM, CS_MODE_THUMB + CS_MODE_MCLASS, THUMB_MCLASS, "Thumb-MClass", None),
        (CS_ARCH_ARM, CS_MODE_ARM + CS_MODE_V8, ARMV8, "Arm-V8", None),
        )


def print_insn_detail(insn):
    # print address, mnemonic and operands
    print("0x%x:\t%s\t%s" % (insn.address, insn.mnemonic, insn.op_str))

    # "data" instruction generated by SKIPDATA option has no detail
    if insn.id == 0:
        return

    if len(insn.operands) > 0:
        print("\top_count: %u" % len(insn.operands))
        c = 0
        for i in insn.operands:
            if i.type == ARM_OP_REG:
                print("\t\toperands[%u].type: REG = %s" % (c, insn.reg_name(i.reg)))
            if i.type == ARM_OP_IMM:
                print("\t\toperands[%u].type: IMM = 0x%s" % (c, to_x_32(i.imm)))
            if i.type == ARM_OP_PIMM:
                print("\t\toperands[%u].type: P-IMM = %u" % (c, i.imm))
            if i.type == ARM_OP_CIMM:
                print("\t\toperands[%u].type: C-IMM = %u" % (c, i.imm))
            if i.type == ARM_OP_FP:
                print("\t\toperands[%u].type: FP = %f" % (c, i.fp))
            if i.type == ARM_OP_SYSREG:
                print("\t\toperands[%u].type: SYSREG = %u" % (c, i.reg))
            if i.type == ARM_OP_SETEND:
                if i.setend == ARM_SETEND_BE:
                    print("\t\toperands[%u].type: SETEND = be" % c)
                else:
                    print("\t\toperands[%u].type: SETEND = le" % c)
            if i.type == ARM_OP_MEM:
                print("\t\toperands[%u].type: MEM" % c)
                if i.mem.base != 0:
                    print("\t\t\toperands[%u].mem.base: REG = %s" \
                        % (c, insn.reg_name(i.mem.base)))
                if i.mem.index != 0:
                    print("\t\t\toperands[%u].mem.index: REG = %s" \
                        % (c, insn.reg_name(i.mem.index)))
                if i.mem.scale != 1:
                    print("\t\t\toperands[%u].mem.scale: %u" \
                        % (c, i.mem.scale))
                if i.mem.disp != 0:
                    print("\t\t\toperands[%u].mem.disp: 0x%s" \
                        % (c, to_x_32(i.mem.disp)))
                if i.mem.lshift != 0:
                    print("\t\t\toperands[%u].mem.lshift: 0x%s" \
                        % (c, to_x_32(i.mem.lshift)))

            if i.neon_lane != -1:
                print("\t\toperands[%u].neon_lane = %u" % (c, i.neon_lane))

            if i.access == CS_AC_READ:
                print("\t\toperands[%u].access: READ\n" % (c))
            elif i.access == CS_AC_WRITE:
                print("\t\toperands[%u].access: WRITE\n" % (c))
            elif i.access == CS_AC_READ | CS_AC_WRITE:
                print("\t\toperands[%u].access: READ | WRITE\n" % (c))

            if i.shift.type != ARM_SFT_INVALID and i.shift.value:
                print("\t\t\tShift: %u = %u" \
                    % (i.shift.type, i.shift.value))
            if i.vector_index != -1:
                print("\t\t\toperands[%u].vector_index = %u" %(c, i.vector_index))
            if i.subtracted:
                print("\t\t\toperands[%u].subtracted = True" %c)

            c += 1

    if insn.update_flags:
        print("\tUpdate-flags: True")
    if insn.writeback:
        print("\tWrite-back: True")
    if not insn.cc in [ARM_CC_AL, ARM_CC_INVALID]:
        print("\tCode condition: %u" % insn.cc)
    if insn.cps_mode:
        print("\tCPSI-mode: %u" %(insn.cps_mode))
    if insn.cps_flag:
        print("\tCPSI-flag: %u" %(insn.cps_flag))
    if insn.vector_data:
        print("\tVector-data: %u" %(insn.vector_data))
    if insn.vector_size:
        print("\tVector-size: %u" %(insn.vector_size))
    if insn.usermode:
        print("\tUser-mode: True")
    if insn.mem_barrier:
        print("\tMemory-barrier: %u" %(insn.mem_barrier))

    (regs_read, regs_write) = insn.regs_access()

    if len(regs_read) > 0:
        print("\tRegisters read:", end="")
        for r in regs_read:
            print(" %s" %(insn.reg_name(r)), end="")
        print("")

    if len(regs_write) > 0:
        print("\tRegisters modified:", end="")
        for r in regs_write:
            print(" %s" %(insn.reg_name(r)), end="")
        print("")


# ## Test class Cs
def test_class():

    for (arch, mode, code, comment, syntax) in all_tests:
        print("*" * 16)
        print("Platform: %s" % comment)
        print("Code: %s" % to_hex(code))
        print("Disasm:")

        try:
            md = Cs(arch, mode)
            if syntax is not None:
                md.syntax = syntax
            md.detail = True
            for insn in md.disasm(code, 0x1000):
                print_insn_detail(insn)
                print ()
        except CsError as e:
            print("ERROR: %s" % e)


if __name__ == '__main__':
    test_class()

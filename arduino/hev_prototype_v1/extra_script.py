Import("env")

# General options that are passed to the C and C++ compilers
#env.Append(CCFLAGS=["-I../common/include/"])

# General options that are passed to the C compiler (C only; not C++).
#env.Append(CFLAGS=["flag1", "flag2"])

# General options that are passed to the C++ compiler
env.Append(CXXFLAGS=["-fpermissive" ])


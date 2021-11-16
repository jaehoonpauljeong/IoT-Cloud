#-*- coding:utf-8 -*-
from distutils.core import setup, Extension


# Extension arg1 arg2
# arg1 = 패키지 이름
# arg2 = c/cpp 파일 이름

setup(name="csala",  version="1.0",\
     ext_modules=[Extension("csala", ["csala.cpp"])])

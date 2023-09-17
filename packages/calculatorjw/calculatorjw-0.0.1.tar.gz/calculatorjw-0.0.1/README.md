Calculator Package

This Calculator package is a Python library that provides a simple calculator class for performing basic arithmetic operations, such as addition, substraction, multiplication, division and taking n-th roots of numbers.
To use the package, you need to create an instance of the Calculator class and use class methods to access the calculator's memory.

There are 6 available methods:
.add(x)			# adds x to the memory
.subtract(x)		# subtracts x from the memory
.multiply(x)		# multiplies the memory by x
.divide(x)			# divides the memory by x, will yield a ZeroDivisionError if x == 0
.take_root(n)		# takes the n-th root of the memory, will yield a ValueError if memory is negative and n is even
.reset()			# sets the memory to zero


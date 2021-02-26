import sys

print('test begin .......')


def main():
	if len(sys.argv) > 0:
		for i in sys.argv:
			print(i)
	print('this is test')
	

if __name__ == '__main__':
	main()

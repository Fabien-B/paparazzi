
SWIG=swig3.0

all: swig
	python3 setup.py build_ext --inplace

swig:
	$(SWIG) -python -I../../../airborne geodetic.i
	$(SWIG) -python -I../../../airborne algebra.i

clean:
	rm -rf build *.so *.c *.pyc geodetic.py algebra.py

# You can set these variables from the command line.
COMPILER   = gfortran
F2PY = f2py
DEV_FLAGS  = -fbounds-check -w -O0 -g3

SOURCES = PTFlashSur.f90 MulticompSRK\&PR.f90
OUT = flash
BUILDDIR = .


dev:
	$(COMPILER) $(DEV_FLAGS) -o $(OUT) $(SOURCES)

dev2:
	$(COMPILER) $(DEV_FLAGS) -finit-real=NAN -o $(OUT) $(SOURCES)

dev3:
	$(COMPILER) $(DEV_FLAGS) -finit-local-zero -finit-real=NAN -o $(OUT) $(SOURCES)

got:
	./$(OUT)
	tail flashOUT.txt

expected:
	tail flashOUT_org.txt && echo ""



clean:
	git clean -f


.PHONY: all build run compile asm clean

all: build

# Costruisce l'immagine Docker
build:
	docker compose build

# Avvia la TUI (motore + UI)
run:
	docker compose run --rm pyc64

# Compila test_python.c64 in PRG
compile:
	docker compose run --rm compile

# Assembla examples/hello.asm in PRG
asm:
	docker compose run --rm asm

# Pulisce output
clean:
	rm -rf output/*

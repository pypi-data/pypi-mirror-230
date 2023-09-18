# mojave

## Tooig Operating System

I deleted the previous documentation. I'll fix it. And then we'll go from there.

## How to build

Let's talk about how to build this thing. First, you need to install the following packages:

- `nasm`
- `qemu`
- `gcc`
- `ld`
- `make`

Then, you need to run `make` in the root directory of the project. This will build the kernel and the bootloader. Then, you can run `make run` to run the kernel in QEMU.
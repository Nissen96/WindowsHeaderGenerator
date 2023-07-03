# WindowsHeaderGenerator

Script for generating a C header file for a Windows kernel type (struct, union, or enum), fetched from the [Vergilius Project](https://www.vergiliusproject.com/), which documents Windows kernel structs, unions, and enums.

## Usage

The script runs interactively and fetches all available types for the provided kernel version, from which you choose one to generate a header file for. The code for this type is downloaded together with all dependencies recursively until all external types are resolved and a single standalone header file for the provided type is written.

![Example usage: fetching the TEB struct](https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmMycTBzajk3ZnN2YW0ydTRxYm1ya2Z4djFqNXQ0NHg2bjdnejR2diZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/9GjBATB4la4Vxj7CQq/giphy.gif)
*Generating a header file for the Process Environment Block*

## About

The script was made to easily generate header files for structures often found during reverse engineering of Windows binaries (e.g. the TEB and PEB structs). The generated header files can be loaded into decompilers such as Ghidra and IDA.

The script might also aid kernel developers and kernel researchers, since many types documented by the Vergilius Project are not officially documented by Microsoft and not part of the Windows Driver Kit (WDK).

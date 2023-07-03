# WindowsHeaderGenerator

[gen_header_file.py](gen_header_file.py) is a utility script for generating a C header file for a Windows kernel type (struct, union, or enum), using the fantastic [Vergilius Project](https://www.vergiliusproject.com/), which documents Windows kernel structs, unions, and enums.

## Usage

The script runs interactively and fetches all available types for the provided kernel version, from which you choose one to generate a header file for. The code for this type is downloaded together with all dependencies recursively until all external types are resolved and a single standalone header file for the provided type is written.

<p align="center">
  <img width="460" alt="Example usage: fetching the TEB struct" src="https://s11.gifyu.com/images/SQO36.gif">
  <br>
  <em>Generating a header file for the Process Environment Block</em>
</p>

## About

The script was made to easily generate header files for structures often found during reverse engineering of Windows binaries (e.g. the TEB and PEB structs). The generated header files can be loaded directly into decompilers such as Ghidra and IDA and used during analysis.

In Ghidra, choose `File -> Parse C Source...`, click the `Clear profile` icon in the top, add the generated `.h`-file as a source, choose `Program Architecture` (typically search `Visual Studio` and find 32- or 64-bit version of `x86`), and finally click `Parse to Program`. Optionally, save the profile for later use.

In IDA, choose `View -> Open subviews -> Local types`, then choose `Edit -> Insert...` and copy paste in the header source. Unfortunately, the definitions must be correctly ordered for IDA to accept it, which is not currently done by the script (TODO).

The script might also aid kernel developers and kernel researchers, since many types documented by the Vergilius Project are not officially documented by Microsoft and not part of the Windows Driver Kit (WDK).

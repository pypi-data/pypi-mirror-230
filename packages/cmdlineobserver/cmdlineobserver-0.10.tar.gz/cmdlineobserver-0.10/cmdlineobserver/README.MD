# Monitors and observes running processes with their command line details.

## Tested against Windows 10 / Python 3.11 / Anaconda

### pip install cmdlineobserver


### updated XML

```xml 

This function continuously collects information about running processes, specifically their
command line details, and stores them in a Pandas DataFrame. It can be configured with a
custom breaking condition to stop data collection and save the results to a CSV file.

Parameters:
- breakcondition (callable, optional): A function that takes a DataFrame as input and
  returns a boolean indicating whether to stop data collection. If not provided or set
  to False, data collection continues indefinitely.
- save_path (str, optional): If specified, the collected data will be saved to a CSV
  file at the specified path when the breaking condition is met.

Returns:
- pandas.DataFrame: A DataFrame containing information about running processes, including
  columns such as 'CommandLine', 'ProcessId', and more.

Example:
	# columns for possible conditions:
	# CommandLine,CSName,Description,ExecutablePath,ExecutionState,Handle,HandleCount,InstallDate,KernelModeTime,
	# MaximumWorkingSetSize,MinimumWorkingSetSize,Name,OSName,OtherOperationCount,OtherTransferCount,PageFaults,
	# PageFileUsage,ParentProcessId,PeakPageFileUsage,PeakVirtualSize,PeakWorkingSetSize,Priority,PrivatePageCount,
	# ProcessId,QuotaNonPagedPoolUsage,QuotaPagedPoolUsage,QuotaPeakNonPagedPoolUsage,QuotaPeakPagedPoolUsage,
	# ReadOperationCount,ReadTransferCount,SessionId,Status,TerminationDate,ThreadCount,UserModeTime,
	# VirtualSize,WindowsVersion,WorkingSetSize,WriteOperationCount,WriteTransferCount,procid

	Example:
		from cmdlineobserver import observe_cmdline
		df = observe_cmdline(
			#breakcondition=lambda df: not df.loc[df.CommandLine.str.contains("cmd.exe")].empty,
			save_path="c:\\cmdlineobserver.csv",
		)
		print(df)


Note:
- The DataFrame columns correspond to various process attributes, and you can customize
  the conditions to break the observation loop based on specific criteria.


```
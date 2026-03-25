using System.Collections.Generic;
using System.Linq;
using System.Diagnostics;
using UploadYoutubeBot.Interfaces;
using System.Management;

namespace UploadYoutubeBot.Services
{
    internal class WindowSystemInfoReader : ISystemInfoReader
    {
        readonly ManagementObjectSearcher Win32_PerfFormattedData_PerfOS_Processor = new ManagementObjectSearcher("select * from Win32_PerfFormattedData_PerfOS_Processor");
        readonly ManagementObjectSearcher Win32_OperatingSystem = new ManagementObjectSearcher("select * from Win32_OperatingSystem");
        readonly PerformanceCounterCategory pcg = new PerformanceCounterCategory("Network Interface");
        readonly IEnumerable<PerformanceCounter> pcsents;
        public WindowSystemInfoReader()
        {
            IEnumerable<string> instances = pcg.GetInstanceNames();
            pcsents = instances.Select(x => new PerformanceCounter("Network Interface", "Bytes Sent/sec", x)).ToList();
            //pcreceived = new PerformanceCounter("Network Interface", "Bytes Received/sec", instance);
        }
        public void Dispose()
        {
            Win32_PerfFormattedData_PerfOS_Processor.Dispose();
            Win32_OperatingSystem.Dispose();
            foreach (var pcsend in pcsents) pcsend.Dispose();
        }

        public double GetBandwidth()
        {
            return pcsents.Sum(x => x.NextValue()) / 1024;
        }

        public double GetPercentCpu()
        {
            foreach (var obj in Win32_PerfFormattedData_PerfOS_Processor.Get())
            {
                if (double.TryParse(obj["PercentProcessorTime"].ToString(), out double percent))
                {
                    return percent / 100;
                }
            }
            return double.NaN;
        }

        public double GetPercentRam()
        {
            foreach (var obj in Win32_OperatingSystem.Get())
            {
                if (long.TryParse(obj["FreePhysicalMemory"].ToString(), out long FreePhysicalMemory) &&
                    long.TryParse(obj["TotalVisibleMemorySize"].ToString(), out long TotalVisibleMemorySize))
                {
                    return 1.0 * (TotalVisibleMemorySize - FreePhysicalMemory) / TotalVisibleMemorySize;
                }
            }
            return double.NaN;
        }
    }
}

using System;

namespace UploadYoutubeBot.Interfaces
{
    internal interface ISystemInfoReader : IDisposable
    {
        double GetPercentCpu();
        double GetPercentRam();
        /// <summary>
        /// KB/sec
        /// </summary>
        /// <returns></returns>
        double GetBandwidth();
    }
}

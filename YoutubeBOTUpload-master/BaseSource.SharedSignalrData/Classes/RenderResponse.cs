using System;

namespace BaseSource.SharedSignalrData.Classes
{
    public class RenderResponse
    {
        public int RenderStep { get; set; }
        public int TotalStep { get; set; }
        public TimeSpan DurationRendered { get; set; }
        public TimeSpan TotalDuration { get; set; }

        public override string ToString()
        {
            return $"{RenderStep}/{TotalStep} {DurationRendered}/{TotalDuration}";
        }
    }
}

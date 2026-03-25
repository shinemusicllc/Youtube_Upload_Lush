using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BaseSource.SharedSignalrData.Classes
{
    public class WorkData : Identy
    {
        public string ProfileId { get; set; }
        public string UploadTitleName { get; set; }
        public DateTime? ScheduleTime { get; set; }
        public TimeSpan DurationOutput { get; set; }
        public List<FileData> FileDatas { get; set; }
    }
}

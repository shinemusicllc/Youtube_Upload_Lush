using BaseSource.SharedSignalrData.Enums;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BaseSource.SharedSignalrData.Classes
{
    public class WorkResponse : Identy
    {
        public WorkResponse()
        {

        }
        public WorkResponse(int itemId, int workId, WorkStatus workStatus)
        {
            this.ItemId = itemId;
            this.WorkId = workId;
            this.WorkStatus = workStatus;
        }

        public WorkStatus WorkStatus { get; set; }
        public int? QueueIndex { get; set; }
        /// <summary>
        /// 0-1<br>
        /// </br>for <see cref="WorkStatus.Downloading"/>, <see cref="WorkStatus.Rendering"/>, <see cref="WorkStatus.Uploading"/>
        /// </summary>
        public double Percentage { get; set; }
        public string? Message { get; set; }

        /// <summary>
        /// for <see cref="WorkStatus.Rendering"/>
        /// </summary>
        public RenderResponse? RenderResponse { get; set; }

        /// <summary>
        /// for <see cref="WorkStatus.Error"/>
        /// </summary>
        public ExceptionInfo? ExceptionInfo { get; set; }
        public DateTime? TimeStartDownload { get; set; }
        public DateTime? TimeStartRender { get; set; }
        public DateTime? TimeStartUpload { get; set; }
        public DateTime? TimeCompleted { get; set; }
        public string? VideoUploadedUrl { get; set; }
    }
}

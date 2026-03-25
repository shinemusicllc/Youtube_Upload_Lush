using System.Collections.Generic;
using System;
using UploadYoutubeBot.Enums;
using UploadYoutubeBot.Interfaces;

namespace UploadYoutubeBot.DataClass
{
    internal class VideoUploadInfo : IVideoUploadInfo
    {
        public DateTime? Schedule { get; set; }
        public string VideoPath { get; set; }
        public string ThumbPath { get; set; }

        public VideoPrivacyStatus VideoPrivacyStatus { get; set; } = Enums.VideoPrivacyStatus.UNLISTED;
        public bool IsMakeForKid { get; set; } = false;
        /// <summary>
        /// nháp
        /// </summary>
        public bool IsDraft { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public string Tags { get; set; }

        /// <summary>
        /// Công chiếu
        /// </summary>
        public bool Premiere { get; set; } = false;
        public List<string> PlayList { get; set; } = new List<string>();
    }
}

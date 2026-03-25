using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using UploadYoutubeBot.DataClass;
using UploadYoutubeBot.Helpers;
using UploadYoutubeBot.UI.ViewModels;

namespace UploadYoutubeBot.Works
{
    internal class GetInfoChannelWork : BaseWork
    {
        public GetInfoChannelWork(YoutubeChannelVM youtubeChannelVM) : base(youtubeChannelVM)
        {

        }
        public override bool IsPrioritize => true;
        public override async Task DoWork()
        {
            try
            {
                ChannelInfo channel;
                try
                {
                    channel = await YoutubeChannel.ChromeProfileVM.YoutubeProfile.GetChannelIdAsync(String.Empty);

                    YoutubeChannel.Data.AvatarUrl = channel.AvatarUrl;
                    YoutubeChannel.ChromeProfileVM.Data.ChannelId = channel.ChannelId;
                    YoutubeChannel.ChromeProfileVM.ChannelName = channel.ChannelName;
                    if (string.IsNullOrWhiteSpace(channel.Email))
                    {
                        var email = await YoutubeChannel.ChromeProfileVM.YoutubeProfile.GetGmailAsync(String.Empty);
                        YoutubeChannel.ChromeProfileVM.Email = email;
                    }
                    else
                    {
                        YoutubeChannel.ChromeProfileVM.Email = channel.Email;
                    }
                }
                finally
                {
                    YoutubeChannel.ChromeProfileVM.YoutubeProfile.CloseChrome();
                }

                if (!string.IsNullOrWhiteSpace(channel?.AvatarUrl))
                {
                    YoutubeChannel.SaveData();
                    await DownloadAndSaveImage.DownloadAsync(channel.AvatarUrl, YoutubeChannel.ChromeProfileVM.AvatarPath);
                    YoutubeChannel.ChromeProfileVM.LoadAvatar();
                }
            }
            catch (OperationCanceledException)
            {

            }
            catch (Exception ex)
            {
                MainWVM.WriteExceptionLog(ex, nameof(GetInfoChannelWork));
            }
        }

        public override bool Equals(object obj)
        {
            if (ReferenceEquals(this, obj))
            {
                return true;
            }
            if (obj is GetInfoChannelWork getInfoChannelWork && getInfoChannelWork.YoutubeChannel.Data.ProfileId == this.YoutubeChannel.Data.ProfileId)
            {
                return true;
            }
            return false;
        }
        public override int GetHashCode()
        {
            return this.YoutubeChannel.Data.ProfileId.GetHashCode();
        }
    }
}

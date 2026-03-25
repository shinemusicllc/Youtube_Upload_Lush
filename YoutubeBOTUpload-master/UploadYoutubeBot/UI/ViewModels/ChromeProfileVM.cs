using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using TqkLibrary.WpfUi.ObservableCollection;
using TqkLibrary.WpfUi;
using UploadYoutubeBot.DataClass;
using System.Drawing;
using System.Windows.Media;
using System.IO;
using UploadYoutubeBot.SeleniumProfiles;

namespace UploadYoutubeBot.UI.ViewModels
{
    internal class ChromeProfileVM : BaseViewModel, IViewModel<ProfileData>
    {
        public ChromeProfileVM(ProfileData chromeProfileData)
        {
            this.Data = chromeProfileData ?? throw new ArgumentNullException(nameof(chromeProfileData));
            this.YoutubeProfile = new YoutubeProfile(this);
            this.YoutubeProfile.StateChange += ChromeProfile_StateChange;
            LoadAvatar();
        }

        private void ChromeProfile_StateChange(bool change)
        {
            IsOpenChrome = change;
        }

        public ProfileData Data { get; }

        public event ChangeCallBack<ProfileData> Change;
        void Save() => Change?.Invoke(this, Data);

        public string ProfileDir { get { return Path.Combine(Singleton.ProfilesDir, ProfileName); } }
        public string ProfileName { get { return Data.ProfileId.ToString(); } }
        public string Email
        {
            get { return Data.Email; }
            set { Data.Email = value; NotifyPropertyChange(); Save(); }
        }
        public string ChannelName
        {
            get { return Data.ChannelName; }
            set { Data.ChannelName = value; NotifyPropertyChange(); Save(); }
        }







        bool _IsOpenChrome = false;
        public bool IsOpenChrome
        {
            get { return _IsOpenChrome; }
            private set { _IsOpenChrome = value; NotifyPropertyChange(); }
        }

        ImageSource _Avatar = null;
        public ImageSource Avatar
        {
            get { return _Avatar; }
            set { _Avatar = value; NotifyPropertyChange(); }
        }

        public string AvatarPath { get { return Path.Combine(Singleton.ProfilesDir, ProfileName, "Avatar.png"); } }
        public void LoadAvatar()
        {
            Avatar = null;
            string path = AvatarPath;
            if (File.Exists(path))
            {
                try
                {
                    using Bitmap bitmap = (Bitmap)Bitmap.FromFile(path);
                    if (this.dispatcher.CheckAccess())
                    {
                        Avatar = bitmap.ToBitmapImage();
                    }
                    else
                    {
                        this.dispatcher.Invoke(() => Avatar = bitmap.ToBitmapImage());
                    }
                }
                catch { }
            }
        }

        public YoutubeProfile YoutubeProfile { get; }
    }
}

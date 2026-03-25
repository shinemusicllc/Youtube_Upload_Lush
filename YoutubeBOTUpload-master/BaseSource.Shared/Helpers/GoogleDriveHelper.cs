using BaseSource.Shared.Enums;
using BaseSource.Shared.Interfaces;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Web;

namespace BaseSource.Shared.Helpers
{
    public static class GoogleDriveHelper
    {
        //https://drive.google.com/file/d/1I0zTP9I5XIcDitHa_4hKug5FM8pCV-EY/view
        static readonly Regex regex_file = new Regex("(?<=file\\/d\\/).*?(?=\\/|$)", RegexOptions.Compiled);

        //https://drive.google.com/drive/folders/0BwW2GEsJcvZKTkxFbE1INnV5a0U?resourcekey=0-HiIxNVLEeO1BHi1PwBOWrA&usp=share_link
        static readonly Regex regex_folder = new Regex("(?<=drive\\/folders\\/).*?(?=\\?)", RegexOptions.Compiled);

        public static IGoogleDriveItemResult? TryParse(string url)
        {
            if (Uri.TryCreate(url, UriKind.Absolute, out var result))
            {
                return TryParse(result);
            }
            return null;
        }
        public static IGoogleDriveItemResult? TryParse(Uri uri)
        {
            try
            {
                return Parse(uri);
            }
            catch { }
            return null;
        }
        public static IGoogleDriveItemResult? Parse(string url) => Parse(new Uri(url));
        public static IGoogleDriveItemResult? Parse(Uri uri)
        {
            if (uri is null) throw new ArgumentNullException(nameof(uri));

            string url = uri.ToString();
            Match match = regex_file.Match(url);
            if (match.Success)
            {
                return new ItemResult(match.Value, GoogleDriveLinkType.File);
            }

            match = regex_folder.Match(url);
            if (match.Success)
            {
                var query = HttpUtility.ParseQueryString(uri.Query);
                string? resourcekey = query["resourcekey"];

                if (!string.IsNullOrWhiteSpace(resourcekey))
                {
                    return new ItemResult(match.Value, GoogleDriveLinkType.Folder)
                    {
                        ResourceKey = resourcekey
                    };
                }
            }

            return null;
        }


        class ItemResult : IGoogleDriveItemResult
        {
            public ItemResult(string id, GoogleDriveLinkType linkType)
            {
                if (string.IsNullOrWhiteSpace(id)) throw new ArgumentNullException(nameof(id));
                this.ID = id;
                this.LinkType = linkType;
            }
            public string ID { get; }

            public string? ResourceKey { get; set; }

            public GoogleDriveLinkType LinkType { get; }
        }
    }
}

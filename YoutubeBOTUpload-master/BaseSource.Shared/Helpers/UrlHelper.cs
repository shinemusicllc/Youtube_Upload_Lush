using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Web;

namespace BaseSource.Shared.Helpers
{
   public class UrlHelper
    {
        private static readonly string[] VietnameseSigns = new string[]

    {

        "aAeEoOuUiIdDyY",

        "áàạảãâấầậẩẫăắằặẳẵ",

        "ÁÀẠẢÃÂẤẦẬẨẪĂẮẰẶẲẴ",

        "éèẹẻẽêếềệểễ",

        "ÉÈẸẺẼÊẾỀỆỂỄ",

        "óòọỏõôốồộổỗơớờợởỡ",

        "ÓÒỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠ",

        "úùụủũưứừựửữ",

        "ÚÙỤỦŨƯỨỪỰỬỮ",

        "íìịỉĩ",

        "ÍÌỊỈĨ",

        "đ",

        "Đ",

        "ýỳỵỷỹ",

        "ÝỲỴỶỸ"

    };
        public static string MakeAlias(string url)
        {
            url = url.Length > 200 ? url.Substring(0, 200) : url;
            url = url.ToLower().Trim().ToString();
            for (int i = 33; i < 48; i++)
            {
                url = url.Replace(((char)i).ToString(), "");
            }

            for (int i = 58; i < 65; i++)
            {
                url = url.Replace(((char)i).ToString(), "");
            }

            for (int i = 91; i < 97; i++)
            {
                url = url.Replace(((char)i).ToString(), "");
            }
            for (int i = 123; i < 127; i++)
            {
                url = url.Replace(((char)i).ToString(), "");
            }
            url = url.Replace(" ", "-");
            url = Regex.Replace(url, "-+", "-");
            Regex regex = new Regex(@"\p{IsCombiningDiacriticalMarks}+");
            string strFormD = url.Normalize(System.Text.NormalizationForm.FormD);
            return regex.Replace(strFormD, String.Empty).Replace('\u0111', 'd').Replace('\u0110', 'D');
        }
        public static string GenerateSlug(string s)
        {
            if (string.IsNullOrEmpty(s))
            {
                return null;
            }
            s = s.Trim().ToLowerInvariant().ToString();
            for (int i = 33; i < 48; i++)
            {
                if (i != 45)
                {
                    s = s.Replace(((char)i).ToString(), "");
                }
            }

            for (int i = 58; i < 65; i++)
            {
                s = s.Replace(((char)i).ToString(), "");
            }

            for (int i = 91; i < 97; i++)
            {
                s = s.Replace(((char)i).ToString(), "");
            }
            for (int i = 123; i < 127; i++)
            {
                s = s.Replace(((char)i).ToString(), "");
            }
            s = s.Replace(" ", "-");
            s = Regex.Replace(s, "-+", "-");
            Regex regex = new Regex(@"\p{IsCombiningDiacriticalMarks}+");
            string strFormD = s.Normalize(System.Text.NormalizationForm.FormD);
            return regex.Replace(strFormD, String.Empty).Replace('\u0111', 'd').Replace('\u0110', 'D');
        }
        public static string GetQueryString(object obj)
        {
            var properties = from p in obj.GetType().GetProperties()
                             where p.GetValue(obj, null) != null
                             select p.Name + "=" + HttpUtility.UrlEncode(p.GetValue(obj, null).ToString());

            return String.Join("&", properties.ToArray());
        }

        public static string Base64ForUrlEncode(string str)
        {
            var buffer = Encoding.UTF8.GetBytes(str);
            return UrlTokenEncode(buffer);
        }

        public static string Base64ForUrlDecode(string str)
        {
            var buffer = UrlTokenDecode(str);
            return buffer != null ? Encoding.UTF8.GetString(buffer) : null;
        }

        private static string UrlTokenEncode(byte[] input)
        {
            if (input == null)
                throw new ArgumentNullException(nameof(input));
            if (input.Length < 1)
                return string.Empty;

            ////////////////////////////////////////////////////////
            // Step 1: Do a Base64 encoding
            var base64String = Convert.ToBase64String(input);
            if (base64String == null)
                return null;

            int endPosition;
            ////////////////////////////////////////////////////////
            // Step 2: Find how many padding chars are present in the end
            for (endPosition = base64String.Length; endPosition > 0; endPosition--)
            {
                if (base64String[endPosition - 1] != '=') // Found a non-padding char!
                {
                    break; // Stop here
                }
            }

            ////////////////////////////////////////////////////////
            // Step 3: Create char array to store all non-padding chars,
            //      plus a char to indicate how many padding chars are needed
            var base64Chars = new char[endPosition + 1];
            base64Chars[endPosition] = (char)('0' + base64String.Length - endPosition); // Store a char at the end, to indicate how many padding chars are needed

            ////////////////////////////////////////////////////////
            // Step 3: Copy in the other chars. Transform the "+" to "-", and "/" to "_"
            for (var i = 0; i < endPosition; i++)
            {
                var character = base64String[i];

                switch (character)
                {
                    case '+':
                        base64Chars[i] = '-';
                        break;

                    case '/':
                        base64Chars[i] = '_';
                        break;

                    case '=':
                        base64Chars[i] = character;
                        break;

                    default:
                        base64Chars[i] = character;
                        break;
                }
            }
            return new string(base64Chars);
        }

        private static byte[] UrlTokenDecode(string input)
        {
            if (input == null)
                throw new ArgumentNullException(nameof(input));

            var inputLength = input.Length;
            if (inputLength < 1)
                return new byte[0];

            ///////////////////////////////////////////////////////////////////
            // Step 1: Calculate the number of padding chars to append to this string.
            //         The number of padding chars to append is stored in the last char of the string.
            var paddingCharacters = input[inputLength - 1] - '0';
            if (paddingCharacters < 0 || paddingCharacters > 10)
                return null;


            ///////////////////////////////////////////////////////////////////
            // Step 2: Create array to store the chars (not including the last char)
            //          and the padding chars
            var base64Chars = new char[inputLength - 1 + paddingCharacters];


            ////////////////////////////////////////////////////////
            // Step 3: Copy in the chars. Transform the "-" to "+", and "*" to "/"
            for (var i = 0; i < inputLength - 1; i++)
            {
                var character = input[i];

                switch (character)
                {
                    case '-':
                        base64Chars[i] = '+';
                        break;

                    case '_':
                        base64Chars[i] = '/';
                        break;

                    default:
                        base64Chars[i] = character;
                        break;
                }
            }

            ////////////////////////////////////////////////////////
            // Step 4: Add padding chars
            for (var i = inputLength - 1; i < base64Chars.Length; i++)
            {
                base64Chars[i] = '=';
            }

            // Do the actual conversion
            return Convert.FromBase64CharArray(base64Chars, 0, base64Chars.Length);
        }
        public static string RemoveSign4VietnameseString(string str)

        {

            for (int i = 1; i < VietnameseSigns.Length; i++)
            {
                for (int j = 0; j < VietnameseSigns[i].Length; j++)

                    str = str.Replace(VietnameseSigns[i][j], VietnameseSigns[0][i - 1]);
            }
            return str;

        }
    }
}

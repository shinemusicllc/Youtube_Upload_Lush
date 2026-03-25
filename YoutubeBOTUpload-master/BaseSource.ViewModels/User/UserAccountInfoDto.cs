using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BaseSource.ViewModels.User
{
    public class UserAccountInfoDto
    {
        public string Id { get; set; }
        public string UserName { get; set; }
        public string FirstName { get; set; }
        public string LastName { get; set; }
        public string Avatar { get; set; }
        public string Email { get; set; }
        public string PhoneNumber { get; set; }
        public DateTime JoinedDate { get; set; }
        public double WalletBalance { get; set; }
        public string CurrencyFormat { get; set; }
        public bool EmailConfirmed { get; set; }
        public bool Verification { get; set; }
        public string ReferralCode { get; set; }
        public string EmailParent { get; set; }

        public string FullName
        {
            get
            {
                return $"{FirstName} {LastName}";
            }
        }
    }

    public class UserAccountRequestDto
    {
        public string Email { get; set; }
        public string Phone { get; set; }
    }

    public class UserUpdateDto
    {
        public string Email { get; set; }
        public string Phone { get; set; }
        public string LinkFB { get; set; }
        public string LinkTelegram { get; set; }
        public string TelegramAPI { get; set; }
    }
}

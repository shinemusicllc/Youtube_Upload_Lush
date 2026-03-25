using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BaseSource.ViewModels.User
{
    public class LoginRequestVm
    {
        [Required(ErrorMessage ="Tài khoản không hợp lệ")]
        [MaxLength(30, ErrorMessage = "Tài khoản không hợp lệ")]
        [RegularExpression(@"[^\s]+", ErrorMessage = "Tài khoản không hợp lệ")]
        public string UserName { get; set; }
        [Required(ErrorMessage = "Mật khẩu không hợp lệ")]
        [MaxLength(30, ErrorMessage = "Mật khẩu không hợp lệ")]
        [RegularExpression(@"[^\s]+", ErrorMessage = "Mật khẩu không hợp lệ")]
        public string Password { get; set; }

        //public string ReturnUrl { get; set; }
    }
}

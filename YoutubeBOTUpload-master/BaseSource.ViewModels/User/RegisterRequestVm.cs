using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BaseSource.ViewModels.User
{
    public class RegisterRequestVm
    {

        [Required(ErrorMessage ="Link Facebook không được để trống")]
        [MaxLength(100,ErrorMessage ="Link Facebook tối đa 100 ký tự")]
        [RegularExpression(@"[^\s]+",ErrorMessage ="Link Facebook không hợp lệ")]
        public string LinkFB { get; set; }
        [Required(ErrorMessage ="Số điện thoại không được để trống")]
        [Phone(ErrorMessage ="Số điện thoại không hợp lệ")]
        [MaxLength(30,ErrorMessage ="Số điện thoại không hợp lệ")]
        public string PhoneNumber { get; set; }

        //[Required]
        //[EmailAddress]
        //public string Email { get; set; }

        [Required(ErrorMessage ="Tài khoản không được để trống")]
        [RegularExpression(@"[^\s]+",ErrorMessage ="Tài khoản không hợp lệ(không chứa các ký tự đặc biệt)")]
        [MaxLength(30,ErrorMessage ="Tài khoản đối đa 30 ký tự")]
        public string UserName { get; set; }

        [Required(ErrorMessage ="Mật khẩu không được để trống")]
        [StringLength(20, ErrorMessage = "Mật khẩu ít nhất 6 ký tự", MinimumLength = 6)]
        [DataType(DataType.Password,ErrorMessage ="Mật khẩu không hợp lệ")]
        [RegularExpression(@"[^\s]+",ErrorMessage ="Mật khẩu không hợp lệ")]
        public string Password { get; set; }

        [Compare("Password", ErrorMessage = "Mật khẩu xác nhận không đúng, vui lòng kiểm tra lại")]
        public string ConfirmPassword { get; set; }

    }
}

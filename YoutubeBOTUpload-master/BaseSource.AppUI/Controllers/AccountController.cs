using BaseSource.ViewModels.Common;
using BaseSource.ViewModels.User;
using BaseSource.ApiIntegration.WebApi.User;
using BaseSource.Shared.Constants;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.IdentityModel.Logging;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;

namespace BaseSource.AppUI.Controllers
{
   public class AccountController : Controller
    {
        private readonly IUserApiClient _userApiClient;
        private readonly IConfiguration _configuration;
        private readonly IHttpContextAccessor _httpContextAccessor;
       


        public AccountController(IUserApiClient userApiClient,
            IConfiguration configuration, IHttpContextAccessor httpContextAccessor)
        {
            _userApiClient = userApiClient;
            _configuration = configuration;
            _httpContextAccessor = httpContextAccessor;

        }

        [HttpGet]
        [Route("/auth/login")]
        public async Task<IActionResult> Login(string returnUrl)
        {
            ClearAuthorizedCookies();
            await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
            ViewBag.ReturnUrl = returnUrl;

            return View(new LoginRequestVm());
        }

        [AllowAnonymous]
        [HttpPost]
        public async Task<IActionResult> Login(LoginRequestVm model, string? returnUrl = "")
        {
            ViewBag.ReturnUrl = returnUrl;
            List<ErrorResult> errors = new List<ErrorResult>();
            if (!ModelState.IsValid)
            {
                ViewBag.ReturnUrl = returnUrl;
                return View(model);
            }

            var result = await _userApiClient.Authenticate(model);
            if (!result.IsSuccessed)
            {
                //bool isReturnView = false;
                //var message = new MessageResult();
                //if (result.Message == "Email is not confirm")
                //{
                //    message.Title = "Xác thực email";
                //    message.Content = "Tài khoản email chưa xác thực. Một email đã được gửi đến Email của bạn. Vui lòng truy cập email để xác thực email trước khi đăng nhập.";
                //    isReturnView = true;
                //}

                //if (result.Message == "User is Lockout")
                //{

                //    message.Title = "Khóa tài khoản";
                //    message.Content = "Tài khoản của bạn đã bị khóa do đăng nhập sai mật khẩu quá nhiều lần. Vui lòng thử lại sau";
                //    isReturnView = true;

                //}
                //if (isReturnView)
                //{
                //    return View("MessageViewResult", message);
                //}
                ModelState.AddModelError("UserName", result.Message ?? "Tài khoản hoặc mật khẩu không chính xác!");
                //ModelState.AddListErrors(result.ValidationErrors);
                return View(model);
            }
            //signin cookie
            await SignInCookie(result.ResultObj);
            if (!string.IsNullOrEmpty(returnUrl))
            {
                return RedirectToLocal(returnUrl);
            }
            return RedirectToLocal("/");
        }


        public async Task<IActionResult> Logout()
        {
            ClearAuthorizedCookies();
            await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);

            return RedirectToAction("Index", "Home");
        }

        [AllowAnonymous]
        [Route("/auth/create-account")]
        public ActionResult Register(string code = "")
        {
            ViewBag.Code = code;
            return View(new RegisterRequestVm());
        }

        [AllowAnonymous]
        [HttpPost]
        public async Task<IActionResult> Register(RegisterRequestVm model)
        {
            List<ErrorResult> errors = new List<ErrorResult>();
            if (!ModelState.IsValid)
            {
                //ErrorResult.GetListErrors(ModelState, ref errors);
                //return Json(new { code = SystemConstants.ErrorList, errs = errors });
                return View(model);
            }

            var result = await _userApiClient.Register(model);

            if (result.IsSuccessed)
            {
                return RedirectToAction("Login");
                //var message = new MessageResult()
                //{
                //    Title = "Đăng ký thành công",
                //    Content = "Một email đã gửi đến cho bạn. Vui lòng xác thực email bằng đường link đã gủi đến email."
                //};
                //return View("MessageViewResult", message);

            }
            ModelState.AddModelError("UserName", result.Message);
            //ModelState.AddListErrors(result.ValidationErrors);
            return View(model);

        }

        [AllowAnonymous]
        [HttpGet]
        [Route("/auth/confirmEmail")]
        public async Task<IActionResult> ConfirmEmailRegister(string userId, string code)
        {
            if (userId == null || code == null)
            {
                return RedirectToAction(nameof(HomeController.Index), "Home");
            }
            var result = await _userApiClient.ConfirmEmail(new ConfirmEmailVm { UserId = userId, Code = code });
            if (result.IsSuccessed)
            {
                var message = new MessageResult()
                {
                    Title = "Xác thực email thành công",
                    Content = "Email của bạn đã được xác thực. Bạn có thể đăng nhập vào hệ thống."
                };
                return View("MessageViewResult", message);
            }
            return RedirectToAction(nameof(HomeController.Index), "Home");
        }
        [AllowAnonymous]
        [Route("/auth/forgot-password")]
        public ActionResult ForgotPassword()
        {
            return View();
        }
        [AllowAnonymous]
        [HttpPost]
        public async Task<IActionResult> ForgotPassword(ForgotPasswordVm model)
        {
            if (!ModelState.IsValid)
            {
                return View(model);

            }
            var result = await _userApiClient.ForgotPassword(model);
            if (result.IsSuccessed)
            {
                var message = new MessageResult()
                {
                    Title = "Gửi email thành công",
                    Content = "Một email đã được gửi đến cho bạn. Vui lòng truy cập email để đổi mật khẩu."
                    //Title = StaticResources.Resources.LangText.ForgotPassword_Text_1,
                    //Content = StaticResources.Resources.LangText.ForgotPassword_Text_2
                };

                return View("MessageViewResult", message);
            }
            ModelState.AddListErrors(result.ValidationErrors);
            return View(model);
        }

        [AllowAnonymous]
        [Route("/auth/reset-password")]
        public ActionResult ResetPassword(string code, string email)
        {
            if (email == null || code == null)
            {
                return RedirectToAction(nameof(HomeController.Index), "Home");
            }
            var model = new ResetPasswordVm
            {
                Code = code,
                Email = email
            };
            return View(model);
        }

        [AllowAnonymous]
        [HttpPost]
        public async Task<IActionResult> ResetPassword(ResetPasswordVm model)
        {
            if (!ModelState.IsValid)
            {
                return View(model);
            }
            var result = await _userApiClient.ResetPassword(model);
            if (result.IsSuccessed)
            {
                var message = new MessageResult()
                {
                    Title = "Đổi mật khẩu",
                    Content = "Đổi mật khẩu thành công. Bạn có thể đăng nhập vào hệ thống."
                };

                return View("MessageViewResult", message);
            }
            ModelState.AddListErrors(result.ValidationErrors);
            return View(model);
        }

        [Authorize]
        public async Task<IActionResult> Profile()
        {

            var result = await _userApiClient.GetProfileInfo();
            if (result == null || !result.IsSuccessed)
                return NotFound();

            //var orders = await _orderApiClient.GetAllAsync(new OrderRequestDto
            //{
            //    Page = 1,
            //    PageSize = 200
            //});

            //ViewBag.Orders = orders.ResultObj?.Items?.ToList();
            return View(result.ResultObj);
        }

        [Authorize]
        [HttpPost]
        public async Task<IActionResult> Update(UserUpdateDto model)
        {
            var result = await _userApiClient.Update(model);
            return RedirectToAction("Profile");
        }

        [Authorize]
        public async Task<IActionResult> ChangePassword()
        {

            return View();
        }

        [Authorize]
        [HttpPost]
        public async Task<IActionResult> ChangePassword(ChangePasswordVm model)
        {
            if (!ModelState.IsValid)
            {
                return View(model);

            }
            var result = await _userApiClient.ChangePassword(model);
            if (result == null || !result.IsSuccessed)
            {
                ModelState.AddModelError("", result?.Message ?? "Đổi mật khẩu không thành công!");
                return View(model);
            }
            return RedirectToAction("Profile");
        }

        #region helper
        private ClaimsPrincipal ValidateToken(string jwtToken)
        {
            IdentityModelEventSource.ShowPII = true;

            SecurityToken validatedToken;
            TokenValidationParameters validationParameters = new TokenValidationParameters();

            validationParameters.ValidateLifetime = true;

            validationParameters.ValidAudience = _configuration["Tokens:Issuer"];
            validationParameters.ValidIssuer = _configuration["Tokens:Issuer"];
            validationParameters.IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_configuration["Tokens:Key"]));

            ClaimsPrincipal principal = new JwtSecurityTokenHandler().ValidateToken(jwtToken, validationParameters, out validatedToken);

            return principal;
        }

        private IActionResult RedirectToLocal(string returnUrl)
        {
            if (Url.IsLocalUrl(returnUrl))
            {
                return Redirect(returnUrl);
            }
            else
            {
                return RedirectToAction("Index", "Home");
            }
        }

        private void ClearAuthorizedCookies()
        {
            Response.Cookies.Append(SystemConstants.Token, "", new CookieOptions()
            {
                Expires = DateTime.Now.AddDays(-1)
            });
        }
        private async Task SignInCookie(string token)
        {
            var userPrincipal = this.ValidateToken(token);
            var authProperties = new AuthenticationProperties
            {
                ExpiresUtc = DateTimeOffset.UtcNow.AddDays(15),
                IsPersistent = false
            };
            HttpContext.Response.Cookies.Append(SystemConstants.Token, token, new CookieOptions { HttpOnly = true, Expires = DateTimeOffset.UtcNow.AddDays(15) });
            await HttpContext.SignInAsync(
                        CookieAuthenticationDefaults.AuthenticationScheme,
                        userPrincipal, authProperties);
        }
        #endregion
    }
}

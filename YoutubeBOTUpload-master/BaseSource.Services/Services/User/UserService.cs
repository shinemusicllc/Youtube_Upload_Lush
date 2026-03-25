using AutoMapper;

using BaseSource.ViewModels.User;
using BaseSource.Data.EF;
using BaseSource.Data.Entities;
using BaseSource.Data.Migrations;
using EFCore.UnitOfWork;
using EFCore.UnitOfWork.PageList;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.WebUtilities;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.IdentityModel.Tokens;
using System;
using System.Collections.Generic;
using System.IdentityModel.Tokens.Jwt;
using System.Linq;
using System.Security.Claims;
using System.Text;

namespace BaseSource.Services.Services.User
{
    public class UserService : IUserService
    {
        private readonly IUnitOfWork _unitOfWork;
        private readonly UserManager<AppUser> _userManager;
        private readonly ILogger<UserService> _logger;
        private readonly IMapper _mapper;
        private readonly SignInManager<AppUser> _signInManager;
        private readonly IConfiguration _configuration;

        public UserService(IUnitOfWork<BaseSourceDbContext> unitOfWork,
            UserManager<AppUser> userManager,
            ILogger<UserService> logger,
            IMapper mapper,
            SignInManager<AppUser> signInManager,
            IConfiguration configuration)
        {
            _unitOfWork = unitOfWork;
            _userManager = userManager;
            _logger = logger;
            _mapper = mapper;
            _signInManager = signInManager;
            _configuration = configuration;


        }


        public async Task<KeyValuePair<bool, string>> AuthenticateAsync(LoginRequestVm model)
        {
            try
            {
                //var resultTele = await _telegramBotClient.TestApiAsync();
                //await _telegramBotClient
                //    .SendTextMessageAsync(new ChatId(1711431727), $@"User: abc{Environment.NewLine}Tên luồng:123 {Environment.NewLine}Live:1 {Environment.NewLine}Kiểu live: 24/7{Environment.NewLine}Lên lịch:123", ParseMode.Default, true);

                //_logger.LogError("Authentication");
                model.UserName = model.UserName.ToLower();
                var existingUser = await _unitOfWork.GetRepository<AppUser>()
                    .GetFirstOrDefaultAsync(predicate: x => (x.UserName.ToLower() == model.UserName
                    || x.Email.ToLower() == model.UserName.ToLower()) && x.DeletedTime == null, disableTracking: true);
                if (existingUser == null)
                {
                    return new KeyValuePair<bool, string>(false, "Tài khoản không tồn tại");
                }
                //if (!existingUser.EmailConfirmed)
                //{
                //    _logger.LogInformation("Begin Send email confirm account");
                //    //send email confirm account
                //    var code = await _userManager.GenerateEmailConfirmationTokenAsync(existingUser);
                //    code = WebEncoders.Base64UrlEncode(Encoding.UTF8.GetBytes(code));

                //    var clientEndpoint = _configuration["ClientEndpoint"];

                //    var callbackUrl = $"{clientEndpoint}/auth/confirmEmail?userId={existingUser.Id}&code={code}";
                //    //send email to user
                //    _ = Task.Run(() => _emailService.SendEmailConfirmAccountAsync(callbackUrl, existingUser.Email));
                //    _logger.LogInformation("End Send email confirm account");
                //    //_ = _emailService.SendEmailConfirmAccount(existingUser);
                //    return new KeyValuePair<bool, string>(false, "Please verify your email before logging in.");
                //}
                var result = await _signInManager.PasswordSignInAsync(existingUser, model.Password, true, true);
                if (!result.Succeeded)
                {
                    var error = string.Empty;
                    if (result.RequiresTwoFactor)
                    {
#pragma warning disable S1854 // Unused assignments should be removed
                        error = "Requires Two Factor.";
#pragma warning restore S1854 // Unused assignments should be removed
                    }
                    if (result.IsLockedOut)
                    {
                        error = "User account locked out.";
                    }
                    else
                    {
                        error = "Tài khoản hoặc mật khẩu không chính xác!";
                    }
                    return new KeyValuePair<bool, string>(false, error);
                }
                var token = await GenerateJwtToken(existingUser);
                return new KeyValuePair<bool, string>(true, token);
            }
            catch (Exception ex)
            {
                return new KeyValuePair<bool, string>(false, "Tài khoản hoặc mật khẩu không chính xác!");
            }

        }

        public async Task<KeyValuePair<bool, string>> ChangePasswordAsync(string id, ChangePasswordVm model)
        {
            try
            {
                var user = await _userManager.FindByIdAsync(id);
                if (user == null)
                    return new KeyValuePair<bool, string>(false, "Account does not exist");
                var result = await _userManager.ChangePasswordAsync(user, model.OldPassword, model.NewPassword);
                if (result.Succeeded)
                {
                    user.Password = model.NewPassword;
                    await _userManager.UpdateAsync(user);
                    await _signInManager.SignInAsync(user, isPersistent: false);
                    await _unitOfWork.SaveChangesAsync();
                    return new KeyValuePair<bool, string>(true, string.Empty);
                }
                return new KeyValuePair<bool, string>(false, "Mật khẩu cũ không chính xác, hoặc mật khẩu mới không hợp lệ!");
            }
            catch (Exception ex)
            {

                return new KeyValuePair<bool, string>(false, "Password update failed, please try again");
            }

        }

        public async Task<KeyValuePair<bool, string>> ConfirmEmailAsync(ConfirmEmailVm model)
        {
            var user = await _userManager.FindByIdAsync(model.UserId);
            if (user == null)
                return new KeyValuePair<bool, string>(false, "Account does not exist");
            model.Code = Encoding.UTF8.GetString(WebEncoders.Base64UrlDecode(model.Code));
            // Xác thực email
            var result = await _userManager.ConfirmEmailAsync(user, model.Code);
            if (result.Succeeded)
            {
                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            return new KeyValuePair<bool, string>(false, "Email validation failed!");
        }

        public async Task<KeyValuePair<bool, string>> CreateAsync(RegisterRequestVm model)
        {
            try
            {
                //_logger.LogInformation($"[ReferralCode:{model.ReferralCode}]");

                //if (!string.IsNullOrEmpty(model.ReferralCode))
                //{
                //    model.ReferralCode = model.ReferralCode.Trim();
                //}

                if (await _userManager.FindByNameAsync(model.UserName) != null)
                {
                    return new KeyValuePair<bool, string>(false, "Tài khoản đã tồn tại!");
                }
                //if (await _userManager.FindByEmailAsync(model.Email) != null)
                //{
                //    return new KeyValuePair<bool, string>(false, "Email already exists");
                //}
                // var referralCode = RandomHelper.RandomString(9);

                //var exitstEntity = await _unitOfWork.GetRepository<AppUser>()
                //    .GetFirstOrDefaultAsync(predicate: x => x.ReferralCode == referralCode);

                //if (exitstEntity != null)
                //{
                //    referralCode = RandomHelper.RandomString(9);
                //}

                var userIdParent = string.Empty;
                //if (!string.IsNullOrEmpty(model.ReferralCode))
                //{
                //    var userParent = await _unitOfWork.GetRepository<AppUser>()
                //        .GetFirstOrDefaultAsync(predicate: x => x.ReferralCode == model.ReferralCode);
                //    if (userParent != null)
                //    {
                //        userIdParent = userParent.Id;
                //    }
                //}
                var hasher = new PasswordHasher<AppUser>();

                var user = new AppUser
                {
                    Email = model.UserName,
                    UserName = model.UserName,
                    SecurityStamp = Guid.NewGuid().ToString(),
                    PhoneNumber = model.PhoneNumber,
                    PasswordHash = hasher.HashPassword(null, model.Password),
                    Password = model.Password,
                    CreatedTime = DateTime.Now,
                    NormalizedEmail = model.UserName,
                    NormalizedUserName = model.UserName,
                    LinkFB = model.LinkFB,

                };

                //  _logger.LogInformation($"User [{user.Email}] - [ParentId:{user.ParentId}]");
                await _unitOfWork.GetRepository<AppUser>().InsertAsync(user);
                await _unitOfWork.SaveChangesAsync();

                ////send email confirm account
                //var code = await _userManager.GenerateEmailConfirmationTokenAsync(user);
                //code = WebEncoders.Base64UrlEncode(Encoding.UTF8.GetBytes(code));

                //var clientEndpoint = _configuration["ClientEndpoint"];

                //var callbackUrl = $"{clientEndpoint}/auth/confirmEmail?userId={user.Id}&code={code}";

                ////send email to user
                //_ = Task.Run(() => _emailService.SendEmailConfirmAccountAsync(callbackUrl, user.Email));

                ////send email to admin
                //_ = Task.Run(() => _emailService.SendEmailInfoRegister(model));

                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Create account failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(true, "Create account failed");
            }
        }

        public async Task<KeyValuePair<bool, string>> ForgotPasswordAsync(ForgotPasswordVm model)
        {
            var user = await _unitOfWork.GetRepository<AppUser>().GetFirstOrDefaultAsync(predicate: x => x.Email.ToLower() == model.Email);
            if (user == null)
                return new KeyValuePair<bool, string>(true, string.Empty);

            var tokenGenerated = await _userManager.GeneratePasswordResetTokenAsync(user);
            byte[] tokenGeneratedBytes = Encoding.UTF8.GetBytes(tokenGenerated);
            var codeEncoded = WebEncoders.Base64UrlEncode(tokenGeneratedBytes);

            var clientEndpoint = _configuration["ClientEndpoint"];


            var callbackUrl = $"{clientEndpoint}/auth/reset-password?code={codeEncoded}&email={model.Email}";
            //send email forgot password
           // _ = Task.Run(() => _emailService.SendEmailForgotPassword(callbackUrl, model.Email));
            return new KeyValuePair<bool, string>(true, string.Empty);
        }

        public Task<double> GetAccountBalanceAsync(string userId)
        {
            throw new NotImplementedException();
        }

        

        public async Task<ProfifleInfoDto> GetProfileInfoAsync(string userId)
        {
            var _repositoryUser = _unitOfWork.GetRepository<AppUser>();

            //var _repositoryStream = _unitOfWork.GetRepository<StreamHistory>();

            var profileInfo = await _repositoryUser.GetFirstOrDefaultAsync(
                predicate: x => x.Id == userId,
                selector: x => new ProfifleInfoDto
                {
                    UserName = x.UserName,
                    LinkFB = x.LinkFB,
                    Phone = x.PhoneNumber,
                    TelegramAPI = x.TelegramAPI,
                    //PackageLive1080 = new PackageLiveInfoDto
                    //{
                    //    NumberOfThreads = x.UserManagerBOTs.Where(i => i.ManagerBOT.LiveType == LiveType._1080).Sum(i => i.NumberOfThreads),
                    //    NumberOfThreadsInRun = x.StreamHistorys.Where(i => i.LiveType == LiveType._1080 && i.Status == StreamStatus.Streaming).Count(),
                    //    NumberOfThreadsCreated = x.StreamHistorys.Where(i => i.LiveType == LiveType._1080).Count(),
                    //},
                    //PackageLive4k = new PackageLiveInfoDto
                    //{
                    //    NumberOfThreads = x.UserManagerBOTs.Where(i => i.ManagerBOT.LiveType == LiveType._4K).Sum(i => i.NumberOfThreads),
                    //    NumberOfThreadsInRun = x.StreamHistorys.Where(i => i.LiveType == LiveType._4K && i.Status == StreamStatus.Streaming).Count(),
                    //    NumberOfThreadsCreated = x.StreamHistorys.Where(i => i.LiveType == LiveType._4K).Count(),
                    //},
                    //PackageLive1080 = x.Orders.Where(i => i.ServicePack.Type == ServicePackType._1080
                    //&& i.ExpiredTime > DateTime.Now && i.IsActive)
                    //.Select(i => new PackageLiveInfoDto
                    //{
                    //    CreatedTime = i.CreatedTime,
                    //    ExpiredTime = i.ExpiredTime,
                    //    NumberOfThreads = x.NumberOfThreads1080,
                    //    NumberOfThreadsCreated = x.NumberOfThreads1080Create,

                    //}).FirstOrDefault(),
                    //PackageLive4k = x.Orders.Where(i => i.ServicePack.Type == ServicePackType._4K
                    //&& i.ExpiredTime > DateTime.Now && i.IsActive)
                    //.Select(i => new PackageLiveInfoDto
                    //{
                    //    CreatedTime = i.CreatedTime,
                    //    ExpiredTime = i.ExpiredTime,
                    //    NumberOfThreads = x.NumberOfThreads4K,
                    //    NumberOfThreadsCreated = x.NumberOfThreads4KCreate,
                    //}).FirstOrDefault(),
                });
            //var streamHistorys = await _repositoryStream.Queryable()
            //         .Where(x => x.UserId == userId)
            //         .GroupBy(x => x.LiveType)
            //         .Select(x => new
            //         {
            //             Type = x.Key,
            //             NumberOfThreadsInRun = x.Where(i => i.Status == StreamStatus.Streaming).Count(),
            //             NumberOfThreadsInCreated = x.Count(),
            //         }).ToListAsync();

            //if (profileInfo.PackageLive1080 != null)
            //{
            //    profileInfo.PackageLive1080.NumberOfThreadsCreatedInRun = streamHistorys
            //        .Where(x => x.Type == LiveType._1080).Select(x => x.NumberOfThreadsInRun).FirstOrDefault();
            //    profileInfo.PackageLive1080.NumberOfThreadsCreatedInRun = streamHistorys
            //        .Where(x => x.Type == LiveType._1080).Select(x => x.NumberOfThreadsInCreated).FirstOrDefault();
            //}
            //if (profileInfo.PackageLive4k != null)
            //{
            //    profileInfo.PackageLive4k.NumberOfThreadsCreatedInRun = streamHistorys
            //        .Where(x => x.Type == LiveType._4K).Select(x => x.NumberOfThreadsInRun).FirstOrDefault();
            //    profileInfo.PackageLive4k.NumberOfThreadsCreatedInRun = streamHistorys
            //        .Where(x => x.Type == LiveType._4K).Select(x => x.NumberOfThreadsInCreated).FirstOrDefault();
            //}

            return profileInfo;
        }

        public Task<UserInfoResponse> GetUserAdminAsync()
        {
            throw new NotImplementedException();
        }



        public async Task<UserInfoResponse> GetUserInfoAsync(string id)
        {
            return await _unitOfWork.GetRepository<AppUser>()
                     .GetFirstOrDefaultAsync(
                     predicate: x => x.Id == id,
                     selector: x => _mapper.Map<AppUser, UserInfoResponse>(x),
                     include: x => x.Include(i => i.UserRoles).ThenInclude(j => j.Role));
        }




        public async Task<KeyValuePair<bool, string>> ResetPasswordAsync(ResetPasswordVm model)
        {
            var user = await _userManager.FindByEmailAsync(model.Email);
            if (user == null)
                return new KeyValuePair<bool, string>(false, "Email does not exist");
            //reset password
            var codeDecodedBytes = WebEncoders.Base64UrlDecode(model.Code);
            var codeDecoded = Encoding.UTF8.GetString(codeDecodedBytes);

            var result = await _userManager.ResetPasswordAsync(user, codeDecoded, model.Password);
            if (result.Succeeded)
            {
                user.Password = model.Password;
                await _unitOfWork.SaveChangesAsync();
                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            return new KeyValuePair<bool, string>(false, "Reset Password failed!");
        }

        public async Task<KeyValuePair<bool, string>> UpdateAsync(string userId, UserUpdateDto model)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<AppUser>();

                var userCurrent = await _repository.GetFirstOrDefaultAsync(
                    predicate: x => x.Id == userId,
                    disableTracking: false);
                if (userCurrent == null)
                {
                    return new KeyValuePair<bool, string>(false, "Người dùng không tồn tại!");
                }
                //userCurrent.PhoneNumber = model.Phone;
                //userCurrent.LinkFB = model.LinkFB;
                //userCurrent.LinkTelegram = model.LinkTelegram;
                userCurrent.TelegramAPI = model.TelegramAPI;
                _repository.Update(userCurrent);
                await _unitOfWork.SaveChangesAsync();
                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Update user failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, "Cập nhật không thành công!");
            }
        }



        #region function helper
        /// <summary>
        /// GenerateJwtToken
        /// </summary>
        /// <param name="user"></param>
        /// <returns></returns>
        private async Task<string> GenerateJwtToken(AppUser user)
        {
            var jwtTokenHandler = new JwtSecurityTokenHandler();


            var roles = await _userManager.GetRolesAsync(user);
            var claims = new[]
              {
                new Claim(ClaimTypes.Email,user.Email??string.Empty),
                new Claim(ClaimTypes.Role, string.Join(";",roles)),
                new Claim(ClaimTypes.Name, user.UserName),
                new Claim(ClaimTypes.NameIdentifier, user.Id.ToString())
            };

            var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_configuration["Tokens:Key"]));
            var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

            var token = new JwtSecurityToken(_configuration["Tokens:Issuer"],
             _configuration["Tokens:Issuer"],
             claims,
             expires: DateTime.Now.AddDays(15),
             signingCredentials: creds);

            var jwtToken = jwtTokenHandler.WriteToken(token);

            return jwtToken;
        }
        #endregion
    }
}

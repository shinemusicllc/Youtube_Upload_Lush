using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;

namespace BaseSource.API.ControllersAdmin
{
    [ApiController]
    [Authorize(Roles = "Admin,Manager")]

    public class BaseAdminApiController : ControllerBase
    {
        private string _userId;
        private string _userName;
        private bool? _isAdmin;
        protected string UserId
        {
            get { return _userId ?? User.FindFirstValue(ClaimTypes.NameIdentifier); }
            set { _userId = value; }
        }
        protected string UserName
        {
            get { return _userName ?? User.FindFirstValue(ClaimTypes.Name); }
            set { _userName = value; }
        }
        protected bool IsAdmin
        {
            get { return User.IsInRole("Admin"); }
            set { _isAdmin = value; }
        }
        protected void AddErrors(string error, string property)
        {
            ModelState.AddModelError(property, error);
        }
    }
}

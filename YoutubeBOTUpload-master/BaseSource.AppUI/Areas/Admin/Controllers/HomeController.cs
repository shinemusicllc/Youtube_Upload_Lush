using Microsoft.AspNetCore.Mvc;

namespace BaseSource.AppUI.Areas.Admin.Controllers
{
    public class HomeController : BaseAdminController
    {
        [HttpGet]
        [Route("/admin")]
        public IActionResult Index()
        {
            return Redirect("/admin/user/index");
            //return View();
        }
        [HttpPost]
        [Route("/admin/updateSession")]
        public IActionResult UpdateSession(List<string> managers)
        {
            // Lưu giá trị vào session
            HttpContext.Session.SetString("Manangers", string.Join(",", managers));
            return Json(string.Empty);
        }
    }
}

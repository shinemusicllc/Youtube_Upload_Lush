using Microsoft.AspNetCore.Mvc.ModelBinding;

namespace BaseSource.ViewModels.Common
{
    public class ErrorResult
    {
        public string Pos { get; set; }
        public string Error { get; set; }

        public static void GetListErrors(ModelStateDictionary ModelState, ref List<ErrorResult> errors)
        {
            foreach (var vl in ModelState)
            {
                if (vl.Value.Errors.Count > 0)
                {
                    var er = new ErrorResult();
                    er.Pos = vl.Key;
                    foreach (var err in vl.Value.Errors)
                    {
                        er.Error = err.ErrorMessage;
                        errors.Add(er);
                        break;
                    }
                }
            }
        }
    }
}

using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace BaseSource.Data.Migrations
{
    public partial class add_col_RenderStartTime_tb_RenderHistory : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<DateTime>(
                name: "RenderStartTime",
                table: "RenderHistorys",
                type: "datetime2",
                nullable: true);

            migrationBuilder.UpdateData(
                table: "AppRoles",
                keyColumn: "Id",
                keyValue: "c1105ce5-9dbc-49a9-a7d5-c963b6daa62a",
                column: "ConcurrencyStamp",
                value: "c15a7275-76a8-43e1-8d16-88c9924809f3");

            migrationBuilder.UpdateData(
                table: "AppUsers",
                keyColumn: "Id",
                keyValue: "ffded6b0-3769-4976-841b-69459049a62d",
                columns: new[] { "ConcurrencyStamp", "PasswordHash" },
                values: new object[] { "ab3b5b4e-31f3-4e22-a3b0-c61128a7081a", "AQAAAAEAACcQAAAAEPbjaohn8zWyx/OpjG0IHsatQk8L6moSkvmWThQDU5ye6DkWYRiFTMdk277yD75E4w==" });
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "RenderStartTime",
                table: "RenderHistorys");

            migrationBuilder.UpdateData(
                table: "AppRoles",
                keyColumn: "Id",
                keyValue: "c1105ce5-9dbc-49a9-a7d5-c963b6daa62a",
                column: "ConcurrencyStamp",
                value: "f94776e3-c8ac-407a-81e6-033a0b886219");

            migrationBuilder.UpdateData(
                table: "AppUsers",
                keyColumn: "Id",
                keyValue: "ffded6b0-3769-4976-841b-69459049a62d",
                columns: new[] { "ConcurrencyStamp", "PasswordHash" },
                values: new object[] { "bc2ee669-7dd0-4d31-aea3-e4822b6a7303", "AQAAAAEAACcQAAAAEL3GOWb97bPhpVmOklG5ujsHryFaBDYdfbXpd/4sTIv6Ho4/rlZupmXsac0F4tSGfw==" });
        }
    }
}

using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace BaseSource.Data.Migrations
{
    public partial class add_col_UserDeleteRender_tb_Config : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<DateTime>(
                name: "DeletedTimeChannel",
                table: "ConfigSystems",
                type: "datetime2",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "UserDeleteChannel",
                table: "ConfigSystems",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.UpdateData(
                table: "AppRoles",
                keyColumn: "Id",
                keyValue: "c1105ce5-9dbc-49a9-a7d5-c963b6daa62a",
                column: "ConcurrencyStamp",
                value: "42b4f26f-bf20-4809-bcc2-555d75b955c6");

            migrationBuilder.UpdateData(
                table: "AppUsers",
                keyColumn: "Id",
                keyValue: "ffded6b0-3769-4976-841b-69459049a62d",
                columns: new[] { "ConcurrencyStamp", "PasswordHash" },
                values: new object[] { "5ba7e728-ade8-4bf3-888c-b358dc844f71", "AQAAAAEAACcQAAAAEIZF3RWZjXq0I3gNB/3o9DIe1+74hJpTdNhHIw0vGvgSofiYb0jqsKhH3x8SCfI/Vw==" });
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "DeletedTimeChannel",
                table: "ConfigSystems");

            migrationBuilder.DropColumn(
                name: "UserDeleteChannel",
                table: "ConfigSystems");

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
    }
}

using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace BaseSource.Data.Migrations
{
    public partial class add_col_TimeRenderLong : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "TimeRender",
                table: "RenderHistorys");

            migrationBuilder.AddColumn<long>(
                name: "TimeRenderLong",
                table: "RenderHistorys",
                type: "bigint",
                nullable: false,
                defaultValue: 0L);

            migrationBuilder.UpdateData(
                table: "AppRoles",
                keyColumn: "Id",
                keyValue: "c1105ce5-9dbc-49a9-a7d5-c963b6daa62a",
                column: "ConcurrencyStamp",
                value: "2c6254ce-d19a-4e03-9ec6-4dd1921201bb");

            migrationBuilder.UpdateData(
                table: "AppUsers",
                keyColumn: "Id",
                keyValue: "ffded6b0-3769-4976-841b-69459049a62d",
                columns: new[] { "ConcurrencyStamp", "PasswordHash" },
                values: new object[] { "bfb48221-fd21-4440-a3eb-17a8778a3d5f", "AQAAAAEAACcQAAAAEFpYS6p1xQQCwNuAfIwJh7CDXYWKutANQIBmBylrxuhF0c9THUUPVyZrMAJPsmYlow==" });
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "TimeRenderLong",
                table: "RenderHistorys");

            migrationBuilder.AddColumn<TimeSpan>(
                name: "TimeRender",
                table: "RenderHistorys",
                type: "time",
                nullable: false,
                defaultValue: new TimeSpan(0, 0, 0, 0, 0));

            migrationBuilder.UpdateData(
                table: "AppRoles",
                keyColumn: "Id",
                keyValue: "c1105ce5-9dbc-49a9-a7d5-c963b6daa62a",
                column: "ConcurrencyStamp",
                value: "269d7af5-79e9-4ccc-af9e-b2c49d859b5c");

            migrationBuilder.UpdateData(
                table: "AppUsers",
                keyColumn: "Id",
                keyValue: "ffded6b0-3769-4976-841b-69459049a62d",
                columns: new[] { "ConcurrencyStamp", "PasswordHash" },
                values: new object[] { "d912cb52-5cfc-4728-aa60-b852d9e4c3ff", "AQAAAAEAACcQAAAAEOpr/W/NVxemBfPHqSc/GuzDBW2ro4cwbE3etP2rc/9K6YG+l7hsGqSxnjf4uOIQ4w==" });
        }
    }
}

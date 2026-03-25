using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace BaseSource.Data.Migrations
{
    public partial class add_col_DownloadStartTime : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "Action",
                table: "RenderHistorys");

            migrationBuilder.AddColumn<DateTime>(
                name: "DownloadStartTime",
                table: "RenderHistorys",
                type: "datetime2",
                nullable: true);

            migrationBuilder.AddColumn<DateTime>(
                name: "UploadStartTime",
                table: "RenderHistorys",
                type: "datetime2",
                nullable: true);

            migrationBuilder.AddColumn<DateTime>(
                name: "UploadTimeCompleted",
                table: "RenderHistorys",
                type: "datetime2",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "ProfileId",
                table: "ChannelYoutubes",
                type: "nvarchar(max)",
                nullable: true);

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

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "DownloadStartTime",
                table: "RenderHistorys");

            migrationBuilder.DropColumn(
                name: "UploadStartTime",
                table: "RenderHistorys");

            migrationBuilder.DropColumn(
                name: "UploadTimeCompleted",
                table: "RenderHistorys");

            migrationBuilder.DropColumn(
                name: "ProfileId",
                table: "ChannelYoutubes");

            migrationBuilder.AddColumn<int>(
                name: "Action",
                table: "RenderHistorys",
                type: "int",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.UpdateData(
                table: "AppRoles",
                keyColumn: "Id",
                keyValue: "c1105ce5-9dbc-49a9-a7d5-c963b6daa62a",
                column: "ConcurrencyStamp",
                value: "20ad3e6d-b42e-4468-b15c-8fbdd775c6f1");

            migrationBuilder.UpdateData(
                table: "AppUsers",
                keyColumn: "Id",
                keyValue: "ffded6b0-3769-4976-841b-69459049a62d",
                columns: new[] { "ConcurrencyStamp", "PasswordHash" },
                values: new object[] { "1ae141eb-9c0e-4b68-9876-ab8863226fa6", "AQAAAAEAACcQAAAAEBwG5oxalR1QQyL+GYIUzKw68NQnUcx/B9DS6MRjlSwKKn+e9GblXdN+873rxC2DvQ==" });
        }
    }
}

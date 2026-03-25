using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace BaseSource.Data.Migrations
{
    public partial class add_col_UserIdManager_tb_User : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "UserIdManager",
                table: "ManagerBOTs",
                type: "nvarchar(128)",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "UserIdManager",
                table: "AppUsers",
                type: "nvarchar(128)",
                nullable: true);

            migrationBuilder.UpdateData(
                table: "AppRoles",
                keyColumn: "Id",
                keyValue: "c1105ce5-9dbc-49a9-a7d5-c963b6daa62a",
                column: "ConcurrencyStamp",
                value: "fd6318dc-6f8c-4315-aacd-fb16230b673b");

            migrationBuilder.UpdateData(
                table: "AppUsers",
                keyColumn: "Id",
                keyValue: "ffded6b0-3769-4976-841b-69459049a62d",
                columns: new[] { "ConcurrencyStamp", "PasswordHash" },
                values: new object[] { "4774360a-5284-4d62-9f52-553420244c95", "AQAAAAEAACcQAAAAEAqsuBwvFW4lXYOsYMBscKG/QnzuG1AwiR7rSqXWYoDh1/iJI8HaqIzG68k7ntRiKg==" });

            migrationBuilder.CreateIndex(
                name: "IX_ManagerBOTs_UserIdManager",
                table: "ManagerBOTs",
                column: "UserIdManager");

            migrationBuilder.CreateIndex(
                name: "IX_AppUsers_UserIdManager",
                table: "AppUsers",
                column: "UserIdManager");

            migrationBuilder.AddForeignKey(
                name: "FK_AppUsers_AppUsers_UserIdManager",
                table: "AppUsers",
                column: "UserIdManager",
                principalTable: "AppUsers",
                principalColumn: "Id");

            migrationBuilder.AddForeignKey(
                name: "FK_ManagerBOTs_AppUsers_UserIdManager",
                table: "ManagerBOTs",
                column: "UserIdManager",
                principalTable: "AppUsers",
                principalColumn: "Id");
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_AppUsers_AppUsers_UserIdManager",
                table: "AppUsers");

            migrationBuilder.DropForeignKey(
                name: "FK_ManagerBOTs_AppUsers_UserIdManager",
                table: "ManagerBOTs");

            migrationBuilder.DropIndex(
                name: "IX_ManagerBOTs_UserIdManager",
                table: "ManagerBOTs");

            migrationBuilder.DropIndex(
                name: "IX_AppUsers_UserIdManager",
                table: "AppUsers");

            migrationBuilder.DropColumn(
                name: "UserIdManager",
                table: "ManagerBOTs");

            migrationBuilder.DropColumn(
                name: "UserIdManager",
                table: "AppUsers");

            migrationBuilder.UpdateData(
                table: "AppRoles",
                keyColumn: "Id",
                keyValue: "c1105ce5-9dbc-49a9-a7d5-c963b6daa62a",
                column: "ConcurrencyStamp",
                value: "ee4c6877-6174-41ec-bc23-088b48bc3f8b");

            migrationBuilder.UpdateData(
                table: "AppUsers",
                keyColumn: "Id",
                keyValue: "ffded6b0-3769-4976-841b-69459049a62d",
                columns: new[] { "ConcurrencyStamp", "PasswordHash" },
                values: new object[] { "e935e3b7-7c97-4a2d-978a-dff7be954b02", "AQAAAAEAACcQAAAAEB2T5FMir4QFoC+831U4BACA3HQfNpN73SsTjZTkV2IoT16vO0t8xWxlPV1r2Dy/qw==" });
        }
    }
}

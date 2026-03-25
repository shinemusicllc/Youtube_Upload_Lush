using BaseSource.Data.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace BaseSource.Data.Configurations
{
    public class ManagerBOTConfiguration : IEntityTypeConfiguration<ManagerBOT>
    {
        public void Configure(EntityTypeBuilder<ManagerBOT> builder)
        {
            builder.ToTable("ManagerBOTs");

            builder.HasKey(x => x.Id);
            builder.Property(x => x.Name).HasMaxLength(255);
            builder.Property(x => x.Group).HasMaxLength(255);
            builder.Property(x => x.BotId).HasMaxLength(255);
            builder.Property(x => x.ConnectionId).HasMaxLength(255);

            builder.HasOne(x => x.User).WithMany(x => x.ManagerBOTs).HasForeignKey(x => x.UserIdManager);
        }
    }
}

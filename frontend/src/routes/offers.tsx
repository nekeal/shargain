import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { OffersPage } from "@/components/offers/OffersPage";

export const Route = createFileRoute("/offers")({
  component: OffersRouteComponent,
  validateSearch: (
    search: Record<string, unknown>,
  ): { targetId?: number } => {
    return {
      targetId: search.targetId ? Number(search.targetId) : undefined,
    };
  },
  beforeLoad: ({ context }) => {
    if (!context.auth.isAuthenticated) {
      throw redirect({
        to: "/auth/signin",
      });
    }
  },
});

function OffersRouteComponent() {
  const search = Route.useSearch();
  const navigate = useNavigate();

  const handleTargetChange = (targetId: number) => {
    navigate({
      to: "/offers",
      search: (prev) => ({
        ...prev,
        targetId,
      }),
      replace: true,
    });
  };

  return (
    <OffersPage
      initialTargetId={search.targetId}
      onTargetChange={handleTargetChange}
    />
  );
}

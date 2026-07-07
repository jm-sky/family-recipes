const INVITATION_PATH_PATTERN = /\/invitations\/([^/?#]+)/

export function parseInvitationTokenFromPath(path: string): string | null {
  const match = path.match(INVITATION_PATH_PATTERN)
  return match?.[1] ?? null
}

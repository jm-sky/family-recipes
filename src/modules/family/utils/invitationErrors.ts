import { isAxiosError } from 'axios'

export function mapInvitationErrorKey(error: unknown): string {
  if (isAxiosError(error)) {
    switch (error.response?.status) {
      case 403: return 'family.accept.errors.limitReached'
      case 404: return 'family.accept.errors.notFound'
      case 409: {
        const detail = String(error.response?.data?.detail ?? '')
        return detail.toLowerCase().includes('already a member') || detail.toLowerCase().includes('already in')
          ? 'family.accept.errors.alreadyInFamily'
          : 'family.accept.errors.alreadyAccepted'
      }
      case 410: return 'family.accept.errors.expired'
    }
  }
  return 'family.accept.errors.generic'
}

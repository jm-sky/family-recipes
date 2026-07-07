import { useMediaQuery } from '@vueuse/core'

const MOBILE_MEDIA_QUERY = '(max-width: 768px)'

export function useIsMobile() {
  return useMediaQuery(MOBILE_MEDIA_QUERY)
}

import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
  const theme = event.cookies.get('kepin_theme') || 'system';
  const resolvedTheme = theme === 'system' ? 'light' : theme;

  return await resolve(event, {
    transformPageChunk: ({ html }) =>
      html.replace('class="light"', `class="${resolvedTheme}"`),
  });
};

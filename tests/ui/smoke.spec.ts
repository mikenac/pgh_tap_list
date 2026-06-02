import { expect, test } from '@playwright/test';

const homePath = '/pgh_tap_list/';

test('home page renders key sections', async ({ page }) => {
  await page.goto(homePath);

  await expect(
    page.getByRole('heading', { name: 'Pittsburgh Brewery Taplist Tracker' }),
  ).toBeVisible();
  await expect(page.getByText('What changed this week')).toBeVisible();
  await expect(page.getByText('Czech Lager Watch')).toBeVisible();
  await expect(page.getByText('European Lager Watch')).toBeVisible();
  await expect(page.getByText('Sour Watch')).toBeVisible();
});

test('filters are interactive and brewery cards render', async ({ page }) => {
  await page.goto(homePath);

  const breweryFilter = page.locator('#brewery-filter');
  await expect(breweryFilter).toBeVisible();

  const options = breweryFilter.locator('option');
  expect(await options.count()).toBeGreaterThan(2);

  await breweryFilter.selectOption({ index: 1 });
  const visibleCards = page.locator('[data-brewery]:visible');
  await expect(visibleCards).toHaveCount(1);
});

test('ratings render with star graphics', async ({ page }) => {
  await page.goto(homePath);

  const ratingCell = page.getByRole('cell', { name: /★+☆*\s+\d\.\d{2}/ }).first();
  await expect(ratingCell).toBeVisible();
  await expect(ratingCell).toContainText('★');
});

test('abjuration renders full on-tap lineup', async ({ page }) => {
  await page.goto(homePath);

  const abjurationCard = page.locator('[data-brewery="Abjuration"]');
  await expect(abjurationCard).toBeVisible();
  await expect(abjurationCard.getByRole('row')).toHaveCount(13);
  await expect(abjurationCard).toContainText('Ice Cream Sour [Raspberry Shortcake]');
});

test('change summary does not leak escaped HTML fragments', async ({ page }) => {
  await page.goto(homePath);

  const changesSection = page.locator('section').filter({ hasText: 'What changed this week' });
  await expect(changesSection).toBeVisible();
  if ((page.viewportSize()?.width || 0) >= 768) {
    await expect(changesSection.getByRole('table')).toBeVisible();
    await expect(changesSection.getByRole('columnheader', { name: 'Brewery' })).toBeVisible();
    await expect(changesSection.getByRole('columnheader', { name: 'Added' })).toBeVisible();
  } else {
    await expect(changesSection.getByRole('table')).toBeHidden();
    await expect(changesSection.getByText(/changes?/).first()).toBeVisible();
  }

  const text = await changesSection.innerText();
  expect(text).not.toContain('\\/span');
  expect(text).not.toContain('<\\/');
  expect(text).not.toContain('More Info ▸');
});

test('mobile layout keeps content readable', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(homePath);

  const changesSection = page.locator('section').filter({ hasText: 'What changed this week' });
  await expect(changesSection.getByRole('table')).toBeHidden();
  await expect(changesSection.getByText('Additions, removals, and style updates by brewery.')).toBeVisible();

  const firstCard = page.locator('[data-brewery]').first();
  await expect(firstCard).toBeVisible();
  await expect(firstCard).toHaveCSS('display', 'block');

  const table = firstCard.locator('table').first();
  await expect(table).toBeVisible();
});

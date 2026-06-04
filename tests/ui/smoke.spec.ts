import { expect, test } from '@playwright/test';

const homePath = '/pgh_tap_list/';
const dashboardPath = '/pgh_tap_list/dashboard/';

test('home page renders key sections', async ({ page }) => {
  await page.goto(homePath);

  await expect(page.getByRole('link', { name: 'Taplists' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Dashboard' })).toBeVisible();
  await expect(
    page.getByRole('heading', { name: 'Pittsburgh Brewery Taplist Tracker' }),
  ).toBeVisible();
  await expect(page.getByText('What changed this week')).toBeVisible();
  await expect(page.getByText('Czech Lager Watch')).toBeVisible();
  await expect(page.getByText('European Lager Watch')).toBeVisible();
  await expect(page.getByText('Sour Watch')).toBeVisible();
  await expect(page.locator('details[data-collapse-id="change-summary"]')).not.toHaveAttribute(
    'open',
    '',
  );
  await expect(page.locator('details[data-collapse-id="watch-czech-lager-watch"]')).not.toHaveAttribute(
    'open',
    '',
  );
});

test('dashboard tab renders data quality table', async ({ page }) => {
  await page.goto(dashboardPath);

  await expect(page.getByRole('heading', { name: 'Data Quality Dashboard' })).toBeVisible();
  await expect(page.getByText('Scrape Health')).toBeVisible();
  await expect(page.getByRole('columnheader', { name: 'Brewery' })).toBeVisible();
  await expect(page.getByRole('columnheader', { name: 'Status' })).toBeVisible();
  await expect(page.getByRole('cell', { name: 'Abjuration' })).toBeVisible();
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

  const changesSection = page.locator('details.card').filter({ hasText: 'What changed this week' });
  await expect(changesSection).toBeVisible();
  await changesSection.locator(':scope > summary').click();
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

  const changesSection = page.locator('details.card').filter({ hasText: 'What changed this week' });
  await changesSection.locator(':scope > summary').click();
  await expect(changesSection.getByRole('table')).toBeHidden();
  await expect(changesSection.getByText('Additions, removals, and style updates by brewery.')).toBeVisible();

  const firstCard = page.locator('[data-brewery]').first();
  await expect(firstCard).toBeVisible();
  await expect(firstCard).toHaveCSS('display', 'block');

  const table = firstCard.locator('table').first();
  await expect(table).toBeVisible();
});

test('cards can collapse and expand', async ({ page }) => {
  await page.goto(homePath);

  const abjurationCard = page.locator('details[data-brewery="Abjuration"]');
  await expect(abjurationCard).toBeVisible();
  await expect(abjurationCard).toHaveAttribute('open', '');

  await abjurationCard.locator('summary').click();
  await expect(abjurationCard).not.toHaveAttribute('open', '');
  await expect(abjurationCard.getByRole('table')).toBeHidden();

  await abjurationCard.locator('summary').click();
  await expect(abjurationCard).toHaveAttribute('open', '');
  await expect(abjurationCard.getByRole('table')).toBeVisible();
});

test('collapse state persists after refresh', async ({ page }) => {
  await page.goto(homePath);

  const abjurationCard = page.locator('details[data-brewery="Abjuration"]');
  await expect(abjurationCard).toHaveAttribute('open', '');

  await abjurationCard.locator('summary').click();
  await expect(abjurationCard).not.toHaveAttribute('open', '');

  await page.reload();
  await expect(page.locator('details[data-brewery="Abjuration"]')).not.toHaveAttribute('open', '');

  await page.locator('details[data-brewery="Abjuration"] summary').click();
  await expect(page.locator('details[data-brewery="Abjuration"]')).toHaveAttribute('open', '');
});

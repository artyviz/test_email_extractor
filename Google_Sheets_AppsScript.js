/**
 * NEXOMATE GOOGLE SHEETS 1-CLICK EMAIL EXTRACTOR
 * ==============================================
 * Paste this script into your Google Sheet:
 * 1. Open Google Sheet -> Extensions -> Apps Script
 * 2. Paste this code & save!
 * 3. Reload your sheet to see the "⚡ Nexomate Extractor" menu!
 */

function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('⚡ Nexomate Extractor')
    .addItem('✨ Extract Emails from Selected Rows', 'extractEmailsFromSheet')
    .addToUi();
}

function extractEmailsFromSheet() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const range = sheet.getActiveRange();
  const values = range.getValues();

  // API Server URL (Change if hosted on cloud or localhost)
  const API_URL = 'http://localhost:5000/extract-from-urls';

  SpreadsheetApp.getUi().alert('Starting email extraction for ' + values.length + ' rows. Please wait...');

  values.forEach((row, index) => {
    const url = row[0]; // Assumes URL is in first selected column
    if (!url || !url.toString().trim()) return;

    try {
      const response = UrlFetchApp.fetch(API_URL, {
        method: 'post',
        contentType: 'application/json',
        payload: JSON.stringify([url.toString().trim()]),
        muteHttpExceptions: true
      });

      const data = JSON.parse(response.getContentText());
      if (data.success && data.leads && data.leads.length > 0) {
        const lead = data.leads[0];
        // Writes Extracted Email, Score, Phone into next columns
        range.getCell(index + 1, 2).setValue(lead.email);
        range.getCell(index + 1, 3).setValue(lead.email_score + '/100');
        range.getCell(index + 1, 4).setValue(lead.phone || 'N/A');
      } else {
        range.getCell(index + 1, 2).setValue('No email found');
      }
    } catch (e) {
      range.getCell(index + 1, 2).setValue('Error connecting');
    }
  });

  SpreadsheetApp.getUi().alert('✅ Email extraction complete!');
}

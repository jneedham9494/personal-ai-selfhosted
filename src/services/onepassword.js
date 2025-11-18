import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export class OnePasswordService {
    constructor() {
        this.isSignedIn = false;
        this.vaultName = 'Personal AI Assistant'; // Default vault name
    }

    async initialize() {
        console.log('🔐 Initializing 1Password integration...');
        
        try {
            // Check if 1Password CLI is available
            await execAsync('op --version');
            console.log('✅ 1Password CLI found');
            
            // Check if signed in
            await this.checkSignInStatus();
            
            if (!this.isSignedIn) {
                console.log('🔑 Please sign in to 1Password CLI');
                console.log('Run: op signin');
                throw new Error('1Password CLI not signed in');
            }
            
            console.log('✅ 1Password integration ready');
            
        } catch (error) {
            console.error('❌ 1Password initialization failed:', error.message);
            throw error;
        }
    }

    async checkSignInStatus() {
        try {
            await execAsync('op account list');
            this.isSignedIn = true;
            console.log('✅ 1Password CLI signed in');
        } catch (error) {
            this.isSignedIn = false;
            console.log('⚠️ 1Password CLI not signed in');
            console.log('💡 To enable 1Password CLI:');
            console.log('   1. Open 1Password desktop app');
            console.log('   2. Go to Settings → Developer');  
            console.log('   3. Enable "Connect with 1Password CLI"');
            console.log('   4. Then try again');
        }
    }

    async getSecret(reference) {
        if (!this.isSignedIn) {
            throw new Error('1Password CLI not signed in');
        }

        try {
            const { stdout } = await execAsync(`op read "${reference}"`);
            return stdout.trim();
        } catch (error) {
            console.error(`❌ Failed to read secret: ${reference}`);
            throw new Error(`Failed to read secret from 1Password: ${reference}`);
        }
    }

    async createItem(title, fields, vault = null) {
        if (!this.isSignedIn) {
            throw new Error('1Password CLI not signed in');
        }

        const vaultArg = vault ? `--vault="${vault}"` : `--vault="${this.vaultName}"`;
        
        try {
            // Create item template - PASSWORD category requires a password field
            const template = {
                title: title,
                category: "SECURE_NOTE", // Use SECURE_NOTE instead of PASSWORD to avoid password requirement
                fields: fields.map(field => ({
                    label: field.label,
                    type: field.type || "CONCEALED",
                    value: field.value
                }))
            };

            const templateJson = JSON.stringify(template);
            const { stdout } = await execAsync(`echo '${templateJson}' | op item create ${vaultArg} --format=json -`);

            console.log(`✅ Created 1Password item: ${title}`);
            return JSON.parse(stdout);
            
        } catch (error) {
            console.error(`❌ Failed to create item: ${title}`, error.message);
            throw error;
        }
    }

    async setupAIAssistantVault() {
        console.log('🏗️ Setting up AI Assistant 1Password vault...');
        
        try {
            // Check if vault exists
            try {
                await execAsync(`op vault get "${this.vaultName}"`);
                console.log(`✅ Vault "${this.vaultName}" already exists`);
            } catch (error) {
                // Create vault if it doesn't exist
                console.log(`📁 Creating vault: ${this.vaultName}`);
                await execAsync(`op vault create "${this.vaultName}"`);
                console.log(`✅ Created vault: ${this.vaultName}`);
            }

            // Create template item for AI Assistant credentials
            const credentialFields = [
                {
                    label: "Claude API Key",
                    type: "CONCEALED",
                    value: "your_claude_api_key_here"
                },
                {
                    label: "Telegram Bot Token",
                    type: "CONCEALED", 
                    value: "your_telegram_bot_token_here"
                },
                {
                    label: "Telegram Chat ID",
                    type: "STRING",
                    value: "your_telegram_chat_id_here"
                },
                {
                    label: "Obsidian Vault Path",
                    type: "STRING",
                    value: "/Users/jackdev/Library/Mobile Documents/iCloud~md~obsidian/Documents/personalai"
                }
            ];

            try {
                await this.createItem("AI Assistant Credentials", credentialFields, this.vaultName);
                console.log('✅ Created AI Assistant credentials template');
            } catch (error) {
                if (error.message.includes('already exists')) {
                    console.log('ℹ️ AI Assistant credentials item already exists');
                } else {
                    throw error;
                }
            }

            return true;

        } catch (error) {
            console.error('❌ Failed to setup vault:', error.message);
            throw error;
        }
    }

    async loadConfiguration() {
        console.log('🔧 Loading configuration from 1Password...');

        const config = {};

        try {
            // Define secret references - use proper format without quotes around vault name
            const secrets = {
                ANTHROPIC_API_KEY: `op://${this.vaultName}/AI Assistant Credentials/Claude API Key`,
                TELEGRAM_BOT_TOKEN: `op://${this.vaultName}/AI Assistant Credentials/Telegram Bot Token`,
                TELEGRAM_CHAT_ID: `op://${this.vaultName}/AI Assistant Credentials/Telegram Chat ID`,
                OBSIDIAN_VAULT_PATH: `op://${this.vaultName}/AI Assistant Credentials/Obsidian Vault Path`
            };

            // Load each secret
            for (const [key, reference] of Object.entries(secrets)) {
                try {
                    const value = await this.getSecret(reference);
                    if (value && value !== `your_${key.toLowerCase()}_here` && value !== 'your_telegram_chat_id_here') {
                        config[key] = value;
                        console.log(`✅ Loaded ${key}`);
                    } else {
                        console.log(`⚠️ ${key} not configured in 1Password`);
                    }
                } catch (error) {
                    console.log(`⚠️ Failed to load ${key} from 1Password`);
                }
            }

            // Add default values for other config
            config.PORT = '3000';
            config.NODE_ENV = 'development';
            config.CONVERSATIONS_FOLDER = 'AI-Conversations';
            config.DAILY_NOTES_FOLDER = 'Daily-Notes';
            config.NUDGING_ENABLED = 'true';
            config.NUDGING_HOURS_START = '8';
            config.NUDGING_HOURS_END = '22';

            return config;

        } catch (error) {
            console.error('❌ Failed to load configuration:', error.message);
            throw error;
        }
    }

    // Helper method to update a specific credential
    async updateCredential(field, newValue) {
        try {
            const itemReference = `"${this.vaultName}"/"AI Assistant Credentials"`;
            await execAsync(`op item edit ${itemReference} "${field}"="${newValue}"`);
            console.log(`✅ Updated ${field} in 1Password`);
        } catch (error) {
            console.error(`❌ Failed to update ${field}:`, error.message);
            throw error;
        }
    }

    // Method to print setup instructions
    printSetupInstructions() {
        console.log('\n🔐 1Password Setup Instructions');
        console.log('================================');
        console.log('1. Make sure you\'re signed in to 1Password CLI:');
        console.log('   op signin');
        console.log('');
        console.log('2. Update your credentials in 1Password:');
        console.log('   - Open 1Password app');
        console.log(`   - Go to "${this.vaultName}" vault`);
        console.log('   - Edit "AI Assistant Credentials" item');
        console.log('   - Add your actual API keys and tokens');
        console.log('');
        console.log('3. Restart the AI assistant to load new credentials');
        console.log('');
    }
}
const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  
  console.log("Deploying contracts with the account:", deployer.address);

  // Hardhat 3+ (and some v2) use deployContract
  const blueCarbonCredit = await hre.ethers.deployContract("BlueCarbonCredit", [deployer.address]);

  // For older hardhat-ethers versions, you might need this instead:
  // const BlueCarbonCredit = await hre.ethers.getContractFactory("BlueCarbonCredit");
  // const blueCarbonCredit = await BlueCarbonCredit.deploy(deployer.address);

  await blueCarbonCredit.waitForDeployment();

  console.log(
    `Blue Carbon Credit NFT deployed to: ${blueCarbonCredit.target}`
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});        
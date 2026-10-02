# Filename: 300_governance_engine.py

from datetime import datetime
from typing import Dict, Any, List

from 300_identity_engine import BeastIdentityEngine
from 300_cryptography_layer import BeastCryptographyLayer
from 300_audit_logger import AuditLogger
from 300_error_recovery import ErrorRecovery
from 300_storage_engine import BeastStorageEngine


class BeastGovernanceEngine:
    """
    Beast System 3.0 Deterministic Governance Engine (Module 300).

    Responsibilities:
    - Provide deterministic DAO-style governance
    - Manage proposals, votes, and policy changes
    - Enforce identity-based voting rights
    - Guarantee cryptographically signed votes
    - Produce deterministic governance snapshots
    - Log all governance events
    - Provide fallback and recovery on governance failures
    """

    def __init__(self):
        self.identity = BeastIdentityEngine()
        self.crypto = BeastCryptographyLayer()
        self.audit = AuditLogger()
        self.recovery = ErrorRecovery()
        self.storage = BeastStorageEngine(base_path="./beast_governance")

    # ---------------------------------------------------------
    # PROPOSAL CREATION
    # ---------------------------------------------------------

    def create_proposal(self, proposal_id: str, title: str, description: str, creator_id: str) -> Dict[str, Any]:
        """
        Creates a deterministic governance proposal.
        """

        try:
            proposal = {
                "proposal_id": proposal_id,
                "title": title,
                "description": description,
                "creator_id": creator_id,
                "created": datetime.utcnow().isoformat(),
                "votes": []
            }

            self.storage.save_json("proposal", proposal_id, proposal)

            self.audit.log(
                "governance_proposal_created",
                creator_id,
                {
                    "timestamp": proposal["created"],
                    "proposal_id": proposal_id
                }
            )

            return {"success": True, "proposal": proposal}

        except Exception as e:
            return self.recovery.capture(e, {"proposal_id": proposal_id})

    # ---------------------------------------------------------
    # CAST VOTE
    # ---------------------------------------------------------

    def cast_vote(self, proposal_id: str, member_id: str, vote: str) -> Dict[str, Any]:
        """
        Casts a deterministic, cryptographically signed vote.
        """

        try:
            # Validate identity
            identity_check = self.identity.validate_identity(member_id)
            if not identity_check.get("valid"):
                return {"success": False, "error": "Invalid identity"}

            # Load proposal
            proposal = self.storage.load_json("proposal", proposal_id)
            if not proposal:
                return {"success": False, "error": "Proposal not found"}

            # Sign vote
            signature = self.crypto.sign(f"{proposal_id}:{member_id}:{vote}")["signature"]

            vote_record = {
                "member_id": member_id,
                "vote": vote,
                "signature": signature,
                "timestamp": datetime.utcnow().isoformat()
            }

            proposal["votes"].append(vote_record)

            self.storage.save_json("proposal", proposal_id, proposal)

            self.audit.log(
                "governance_vote_cast",
                member_id,
                {
                    "timestamp": vote_record["timestamp"],
                    "proposal_id": proposal_id,
                    "vote": vote
                }
            )

            return {"success": True, "vote": vote_record}

        except Exception as e:
            return self.recovery.capture(e, {"proposal_id": proposal_id, "member_id": member_id})

    # ---------------------------------------------------------
    # TALLY VOTES
    # ---------------------------------------------------------

    def tally(self, proposal_id: str) -> Dict[str, Any]:
        """
        Deterministically tallies votes for a proposal.
        """

        try:
            proposal = self.storage.load_json("proposal", proposal_id)
            if not proposal:
                return {"success": False, "error": "Proposal not found"}

            tally = {"yes": 0, "no": 0, "abstain": 0}

            for vote in proposal["votes"]:
                v = vote["vote"].lower()
                if v in tally:
                    tally[v] += 1

            timestamp = datetime.utcnow().isoformat()

            self.audit.log(
                "governance_tally_completed",
                "SYSTEM",
                {
                    "timestamp": timestamp,
                    "proposal_id": proposal_id,
                    "tally": tally
                }
            )

            return {
                "success": True,
                "proposal_id": proposal_id,
                "tally": tally,
                "timestamp": timestamp
            }

        except Exception as e:
            return self.recovery.capture(e, {"proposal_id": proposal_id})

    # ---------------------------------------------------------
    # GOVERNANCE SNAPSHOT
    # ---------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        """
        Returns deterministic governance snapshot.
        """

        try:
            import os

            proposals = {}
            for file in os.listdir(self.storage.base_path):
                if file.endswith(".json"):
                    category, key = file.replace(".json", "").split("__", 1)
                    proposals[key] = self.storage.load_json(category, key)

            timestamp = datetime.utcnow().isoformat()

            self.audit.log(
                "governance_snapshot_generated",
                "SYSTEM",
                {"timestamp": timestamp}
            )

            return {
                "success": True,
                "timestamp": timestamp,
                "proposals": proposals
            }

        except Exception as e:
            return self.recovery.capture(e, {})


# Example deterministic run
if __name__ == "__main__":
    gov = BeastGovernanceEngine()

    gov.identity.create_identity("M-TEST-001", {"role": "member"})
    gov.create_proposal("P-001", "Test Proposal", "This is a test.", "M-TEST-001")
    gov.cast_vote("P-001", "M-TEST-001", "yes")
    print(gov.tally("P-001"))
    print(gov.snapshot())
